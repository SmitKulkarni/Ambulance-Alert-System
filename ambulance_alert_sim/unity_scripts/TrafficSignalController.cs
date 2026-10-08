using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// 4-Aspect Traffic Signal States:
/// - Red: Complete halt (all 3 competing approaches)
/// - Yellow: Clearance change interval
/// - Green: Normal cycle proceed (only 1 approach active at a time)
/// - EmergencyBlue: 4th Color! Acoustic siren priority wave for approaching emergency vehicle
/// </summary>
public enum SignalState 
{ 
    Red, 
    Yellow, 
    Green, 
    EmergencyBlue 
}

public enum ApproachDirection 
{ 
    North, 
    East, 
    South, 
    West 
}

[System.Serializable]
public class SignalHead
{
    public ApproachDirection direction;
    public MeshRenderer redBulb;
    public MeshRenderer yellowBulb;
    public MeshRenderer greenBulb;
    public MeshRenderer blueBulb; // 4th Aspect: Emergency Blue Lamp
    public Light emergencySpotlight; // HDR spotlight for blue preemption halo
    [HideInInspector] public SignalState currentState;
}

public class TrafficSignalController : MonoBehaviour
{
    [Header("Signal Heads Configuration (4 Approaches)")]
    public List<SignalHead> signals;

    [Header("Cycle Timings (Seconds)")]
    public float greenDuration = 8.0f;
    public float yellowDuration = 2.5f;

    [Header("Ambulance Signal Hold Duration")]
    public float minEmergencyHoldDuration = 16.0f; // Extended hold window for ambulance transit
    public float postClearanceSafetyBuffer = 3.5f; // Extra clearance buffer before restoring normal signals

    [Header("Glow Emission Materials")]
    public Color redColor = Color.red;
    public Color yellowColor = Color.yellow;
    public Color greenColor = Color.green;
    public Color emergencyBlueColor = new Color(0.0f, 0.83f, 1.0f) * 5.0f; // 4th Color: HDR Cyan-Blue bloom

    [Header("Auditory Warning Alarm for Cross-Traffic (Pedestrians & Stopped Lanes)")]
    public AudioSource crossTrafficWarningAudioSource; // Buzzer/alarm warning others that ambulance is approaching
    public AudioClip crossTrafficAlarmClip;

    [Header("Acoustic Siren Detection Settings")]
    public float sirenDetectionThresholdDb = 75.0f;
    public bool autoAcousticDetectionEnabled = true;

    // Normal Cycle Memory (1-at-a-time Green)
    private int currentNormalPhaseIndex = 0; // 0: North, 1: East, 2: South, 3: West
    private bool isInYellowTransition = false;
    private float savedTimeInPhase = 0f;
    private Coroutine activeCycleCoroutine;

    // Emergency Preemption State
    private bool isEmergencyActive = false;
    private ApproachDirection activeEmergencyApproach;

    void Start()
    {
        activeCycleCoroutine = StartCoroutine(SingleGreenSequentialCycleRoutine());
    }

    /// <summary>
    /// Normal Working: At any time, ONLY ONE signal is GREEN, and the other 3 are SOLID RED.
    /// Order: North Green -> North Yellow -> East Green -> East Yellow -> South Green -> South Yellow -> West Green -> West Yellow -> repeat.
    /// </summary>
    private IEnumerator SingleGreenSequentialCycleRoutine()
    {
        ApproachDirection[] phaseOrder = new ApproachDirection[] 
        { 
            ApproachDirection.North, 
            ApproachDirection.East, 
            ApproachDirection.South, 
            ApproachDirection.West 
        };

        while (!isEmergencyActive)
        {
            ApproachDirection activeDir = phaseOrder[currentNormalPhaseIndex];

            // 1. Set Active Direction to GREEN; All other 3 directions are RED
            isInYellowTransition = false;
            foreach (var sig in signals)
            {
                if (sig.direction == activeDir)
                    ApplyState(sig, SignalState.Green);
                else
                    ApplyState(sig, SignalState.Red);
            }

            for (savedTimeInPhase = 0; savedTimeInPhase < greenDuration; savedTimeInPhase += Time.deltaTime)
                yield return null;

            // 2. Transition Active Direction to YELLOW; Other 3 remain RED
            isInYellowTransition = true;
            foreach (var sig in signals)
            {
                if (sig.direction == activeDir)
                    ApplyState(sig, SignalState.Yellow);
                else
                    ApplyState(sig, SignalState.Red);
            }

            for (savedTimeInPhase = 0; savedTimeInPhase < yellowDuration; savedTimeInPhase += Time.deltaTime)
                yield return null;

            // Advance to next approach in sequential rotation
            currentNormalPhaseIndex = (currentNormalPhaseIndex + 1) % phaseOrder.Length;
        }
    }

    /// <summary>
    /// Automatic Acoustic Siren Sound Detection Callback.
    /// Called when directional microphone array detects siren audio signature above threshold.
    /// </summary>
    public void OnAcousticSirenDetected(ApproachDirection approachingFrom, float decibelLevel)
    {
        if (!autoAcousticDetectionEnabled) return;

        if (decibelLevel >= sirenDetectionThresholdDb)
        {
            Debug.Log($"[ACOUSTIC SENSOR] Siren detected from {approachingFrom} approach at {decibelLevel:F1} dB! Triggering 4th Color BLUE preemption.");
            TriggerEmergencyPreemption(approachingFrom);
        }
    }

    /// <summary>
    /// Emergency Preemption Trigger:
    /// - ONLY the approaching direction turns 4th Color: BLUE (Emergency Priority)
    /// - ALL other 3 directions turn SOLID RED
    /// </summary>
    public void TriggerEmergencyPreemption(ApproachDirection approachingFrom)
    {
        if (isEmergencyActive && activeEmergencyApproach == approachingFrom) 
            return;

        isEmergencyActive = true;
        activeEmergencyApproach = approachingFrom;

        if (activeCycleCoroutine != null)
            StopCoroutine(activeCycleCoroutine);

        // 1. Force ALL 3 competing signal heads to Solid Red to halt cross-traffic
        foreach (var sig in signals)
        {
            if (sig.direction != approachingFrom)
            {
                ApplyState(sig, SignalState.Red);
            }
        }

        // 2. Set ONLY the approaching side to the 4th Color: BLUE
        SignalHead targetHead = signals.Find(s => s.direction == approachingFrom);
        if (targetHead != null)
        {
            ApplyState(targetHead, SignalState.EmergencyBlue);
        }

        // 3. Play auditory warning buzzer/alarm for other lanes and pedestrians
        if (crossTrafficWarningAudioSource != null)
        {
            if (crossTrafficAlarmClip != null) crossTrafficWarningAudioSource.clip = crossTrafficAlarmClip;
            crossTrafficWarningAudioSource.loop = true;
            crossTrafficWarningAudioSource.Play();
        }

        preemptionStartTime = Time.time;
        Debug.Log($"[EVTSP] Preemption Active: {approachingFrom} is 4th-Color BLUE (Holding for min {minEmergencyHoldDuration}s); all 3 others are RED with Auditory Alarm Active.");
    }

    private float preemptionStartTime = 0f;

    /// <summary>
    /// Releases preemption after ambulance clears intersection, respecting extended minimum hold duration.
    /// </summary>
    public void ReleaseEmergencyPreemption()
    {
        if (!isEmergencyActive) return;
        StartCoroutine(HoldAndReleaseRoutine());
    }

    private IEnumerator HoldAndReleaseRoutine()
    {
        // 1. Ensure ambulance priority holds for at least minEmergencyHoldDuration
        float elapsed = Time.time - preemptionStartTime;
        float holdRemaining = Mathf.Max(0f, minEmergencyHoldDuration - elapsed);
        if (holdRemaining > 0f)
        {
            yield return new WaitForSeconds(holdRemaining);
        }

        // 2. Post-clearance safety buffer: hold all red briefly to prevent collision
        foreach (var sig in signals)
            ApplyState(sig, SignalState.Red);
        yield return new WaitForSeconds(postClearanceSafetyBuffer);

        // 3. Stop cross-traffic auditory warning alarm
        if (crossTrafficWarningAudioSource != null && crossTrafficWarningAudioSource.isPlaying)
        {
            crossTrafficWarningAudioSource.Stop();
        }

        isEmergencyActive = false;
        activeCycleCoroutine = StartCoroutine(ResumeNormalCycleRoutine());
    }

    private IEnumerator ResumeNormalCycleRoutine()
    {
        // Resume the remaining time of the interrupted approach
        float targetDuration = isInYellowTransition ? yellowDuration : greenDuration;
        float remaining = Mathf.Max(0f, targetDuration - savedTimeInPhase);

        if (remaining > 0.5f)
        {
            ApproachDirection[] phaseOrder = new ApproachDirection[] 
            { 
                ApproachDirection.North, 
                ApproachDirection.East, 
                ApproachDirection.South, 
                ApproachDirection.West 
            };
            ApproachDirection activeDir = phaseOrder[currentNormalPhaseIndex];
            SignalState resumeState = isInYellowTransition ? SignalState.Yellow : SignalState.Green;

            foreach (var sig in signals)
            {
                if (sig.direction == activeDir)
                    ApplyState(sig, resumeState);
                else
                    ApplyState(sig, SignalState.Red);
            }

            yield return new WaitForSeconds(remaining);
            currentNormalPhaseIndex = (currentNormalPhaseIndex + 1) % phaseOrder.Length;
        }

        activeCycleCoroutine = StartCoroutine(SingleGreenSequentialCycleRoutine());
    }

    private void ApplyState(SignalHead head, SignalState state)
    {
        head.currentState = state;

        // 4 Bulbs: Red, Yellow, Green, and 4th Color BLUE
        SetBulb(head.redBulb,    state == SignalState.Red,           redColor);
        SetBulb(head.yellowBulb, state == SignalState.Yellow,        yellowColor);
        SetBulb(head.greenBulb,  state == SignalState.Green,         greenColor);
        SetBulb(head.blueBulb,   state == SignalState.EmergencyBlue, emergencyBlueColor);

        if (head.emergencySpotlight != null)
        {
            head.emergencySpotlight.enabled = (state == SignalState.EmergencyBlue);
            head.emergencySpotlight.color = new Color(0f, 0.83f, 1f);
        }
    }

    private void SetBulb(MeshRenderer renderer, bool isOn, Color color)
    {
        if (renderer == null) return;
        Material mat = renderer.material;
        if (isOn)
        {
            mat.EnableKeyword("_EMISSION");
            mat.SetColor("_EmissionColor", color);
        }
        else
        {
            mat.DisableKeyword("_EMISSION");
            mat.SetColor("_EmissionColor", Color.black);
        }
    }
}

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Automatic Directional Acoustic Siren Approach Detector for Smart Traffic Signal Controllers.
/// Continuously samples acoustic sound pressure level (dB SPL) across directional microphone arrays
/// and automatically identifies which side an emergency vehicle is approaching from.
/// </summary>
public class AutomaticEmergencyDetector : MonoBehaviour
{
    [Header("Connected Traffic Controller")]
    public TrafficSignalController trafficSignalController;

    [Header("Acoustic Sensor Positions (Distance in meters from intersection center)")]
    public float sensorArmDistance = 25.0f;

    [Header("Detection Parameters")]
    [Tooltip("Threshold in dB SPL to trigger emergency preemption (ambient is ~45 dB)")]
    public float sirenDetectionThresholdDb = 75.0f;
    [Tooltip("Siren reference Sound Pressure Level at 1 meter distance")]
    public float sirenSourceSplAt1m = 120.0f;
    public float atmosphericDamping = 0.005f;

    [Header("Live Sensor Telemetry (Read Only)")]
    [SerializeField] private float northMicDb = 42.0f;
    [SerializeField] private float eastMicDb = 42.0f;
    [SerializeField] private float southMicDb = 42.0f;
    [SerializeField] private float westMicDb = 42.0f;

    [Header("Detection Status")]
    public bool isEmergencyDetected = false;
    public ApproachDirection detectedApproachSide;
    [Range(0f, 1f)] public float detectionConfidence = 0.0f;

    // Directional Microphone Positions in 3D Space
    private Dictionary<ApproachDirection, Vector3> microphonePositions;

    void Awake()
    {
        Vector3 center = transform.position;
        microphonePositions = new Dictionary<ApproachDirection, Vector3>
        {
            { ApproachDirection.North, center + new Vector3(0, 0, sensorArmDistance) },
            { ApproachDirection.East,  center + new Vector3(sensorArmDistance, 0, 0) },
            { ApproachDirection.South, center + new Vector3(0, 0, -sensorArmDistance) },
            { ApproachDirection.West,  center + new Vector3(-sensorArmDistance, 0, 0) }
        };
    }

    void Update()
    {
        ScanAcousticCorridors();
    }

    /// <summary>
    /// Automatic Detection Algorithm:
    /// Samples siren sound pressure levels across all 4 corridors,
    /// identifies peak decibel reading, and automatically triggers preemption on the detected approach.
    /// </summary>
    public void ScanAcousticCorridors()
    {
        // Find all active emergency vehicles in the scene
        AmbulanceVehicle[] ambulances = Object.FindObjectsByType<AmbulanceVehicle>(FindObjectsSortMode.None);

        if (ambulances == null || ambulances.Length == 0)
        {
            ResetToAmbientNoise();
            return;
        }

        // Evaluate acoustic field for the loudest approaching ambulance
        float maxMeasuredDb = 0f;
        ApproachDirection loudestDirection = ApproachDirection.North;

        foreach (var dir in microphonePositions.Keys)
        {
            Vector3 micPos = microphonePositions[dir];
            float combinedSpl = 45.0f; // Ambient urban noise floor (45 dB)

            foreach (var amb in ambulances)
            {
                if (amb == null) continue;

                float dist = Vector3.Distance(micPos, amb.transform.position);
                dist = Mathf.Max(dist, 1.0f); // Guard against zero distance

                // Spherical geometric acoustic decay: SPL(d) = SPL_1m - 20*log10(d) - alpha*d
                float sirenSpl = sirenSourceSplAt1m - (20.0f * Mathf.Log10(dist)) - (atmosphericDamping * dist);
                
                // Logarithmic acoustic energy summation
                combinedSpl = 10.0f * Mathf.Log10(Mathf.Pow(10f, combinedSpl / 10f) + Mathf.Pow(10f, sirenSpl / 10f));
            }

            // Assign to serialized inspection fields
            switch (dir)
            {
                case ApproachDirection.North: northMicDb = combinedSpl; break;
                case ApproachDirection.East:  eastMicDb = combinedSpl; break;
                case ApproachDirection.South: southMicDb = combinedSpl; break;
                case ApproachDirection.West:  westMicDb = combinedSpl; break;
            }

            if (combinedSpl > maxMeasuredDb)
            {
                maxMeasuredDb = combinedSpl;
                loudestDirection = dir;
            }
        }

        // AUTOMATIC DECISION LOGIC:
        if (maxMeasuredDb >= sirenDetectionThresholdDb)
        {
            float margin = maxMeasuredDb - sirenDetectionThresholdDb;
            detectionConfidence = Mathf.Clamp01(0.70f + margin * 0.015f);

            if (!isEmergencyDetected || detectedApproachSide != loudestDirection)
            {
                isEmergencyDetected = true;
                detectedApproachSide = loudestDirection;

                Debug.Log($"[AUTOMATIC DETECTION] 🚨 Siren identified from {detectedApproachSide} approach ({maxMeasuredDb:F1} dB SPL, Confidence: {detectionConfidence*100f:F1}%).");

                // Automatically trigger the 4-Aspect BLUE priority on the detected direction!
                if (trafficSignalController != null)
                {
                    trafficSignalController.TriggerEmergencyPreemption(detectedApproachSide);
                }
            }
        }
        else
        {
            if (isEmergencyDetected)
            {
                isEmergencyDetected = false;
                detectionConfidence = 0.0f;

                if (trafficSignalController != null)
                {
                    trafficSignalController.ReleaseEmergencyPreemption();
                }
            }
        }
    }

    private void ResetToAmbientNoise()
    {
        northMicDb = 42.0f + Mathf.Sin(Time.time) * 3f;
        eastMicDb  = 41.0f + Mathf.Cos(Time.time) * 3f;
        southMicDb = 43.0f + Mathf.Sin(Time.time * 0.8f) * 3f;
        westMicDb  = 42.0f + Mathf.Cos(Time.time * 1.2f) * 3f;

        if (isEmergencyDetected)
        {
            isEmergencyDetected = false;
            detectionConfidence = 0.0f;
            if (trafficSignalController != null)
            {
                trafficSignalController.ReleaseEmergencyPreemption();
            }
        }
    }

    /// <summary>
    /// Draw sensor gizmos in Unity Editor scene view
    /// </summary>
    void OnDrawGizmosSelected()
    {
        if (microphonePositions == null) return;

        foreach (var kvp in microphonePositions)
        {
            Gizmos.color = (isEmergencyDetected && detectedApproachSide == kvp.Key) ? Color.cyan : Color.gray;
            Gizmos.DrawWireSphere(kvp.Value, 2.5f);
            Gizmos.DrawLine(transform.position, kvp.Value);
        }
    }
}

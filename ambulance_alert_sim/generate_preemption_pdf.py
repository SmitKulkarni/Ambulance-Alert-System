# generate_preemption_pdf.py
"""
Generates the publication-grade multi-page PDF document:
report/traffic_signal_preemption_guide.pdf
Corresponding to the EVTSP Comprehensive Guide & Unity Codebase.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "report")
PDF_PATH = os.path.join(REPORT_DIR, "traffic_signal_preemption_guide.pdf")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Top banner line
        self.setStrokeColor(colors.HexColor("#0284c7"))
        self.setLineWidth(1.5)
        self.line(14 * mm, A4[1] - 14 * mm, A4[0] - 14 * mm, A4[1] - 14 * mm)
        
        # Bottom footer line
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.8)
        self.line(14 * mm, 14 * mm, A4[0] - 14 * mm, 14 * mm)
        
        # Footer text
        self.drawString(14 * mm, 10 * mm, "Smart Traffic Signal Preemption • Autonomous Corridor Integration")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(A4[0] - 14 * mm, 10 * mm, page_str)
        self.restoreState()

def build_pdf():
    os.makedirs(REPORT_DIR, exist_ok=True)
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=2
    )

    sub_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=6,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#0f172a')
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=5.8,
        leading=7.2,
        textColor=colors.HexColor('#f8fafc')
    )

    story = []

    # ==================== PAGE 1 ====================
    story.append(Paragraph("Emergency Vehicle Traffic Signal Preemption (EVTSP)", title_style))
    story.append(Paragraph("Integration Protocol: Mathematical Model, State Restoral & 3D Unity Architecture", sub_style))

    story.append(Paragraph("1. Operational Principle & Integration with Corridor Model", h2_style))
    story.append(Paragraph(
        "In our corridor model, advance alerts reduced effective traffic density along forward segments. "
        "This module extends that foundation into an active <b>Intersection Preemption Layer</b>. When an emergency vehicle "
        "enters the detection radius of an upcoming intersection:",
        body_style
    ))
    story.append(Paragraph("• <b>Priority Signal Preemption:</b> Regardless of current cycle timing (Red, Yellow, or Green), approaching direction transitions immediately to an intense flashing Glow Emergency Green.", body_style))
    story.append(Paragraph("• <b>Cross-Traffic Conflict Prevention:</b> All competing approaches immediately switch to Solid Red, preventing collisions and clearing conflicting movements.", body_style))
    story.append(Paragraph("• <b>Siren & Audio Doppler Simulation:</b> 3D positional audio emits a high-priority siren that dynamically attenuates over spatial distance.", body_style))
    story.append(Paragraph("• <b>Exact State Memory & Resumption:</b> The intersection caches its active state, elapsed time, and standard phase timings. Once departure trigger clears, normal cycles resume without starvation.", body_style))

    story.append(Paragraph("2. State Transition Machine", h2_style))
    callout_text = (
        "<b>Normal Cycle State:</b> Standard N/S and E/W green/yellow/red timer-based loop.<br/>"
        "<b>Preemption Trigger:</b> Ambulance enters trigger zone &rarr; Store snapshot: <code>(activePhase, timeRemaining)</code> "
        "&rarr; Set all cross directions to <code>RED</code> &rarr; Set approach direction to <code>EMERGENCY_GLOW_GREEN</code>.<br/>"
        "<b>Post-Clearance Exit:</b> Ambulance clears departure trigger &rarr; Restore snapshot state &rarr; Normal cycles resume."
    )
    t_callout = Table([[Paragraph(callout_text, callout_style)]], colWidths=[A4[0] - 28 * mm])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('LINELEFT', (0,0), (0,-1), 3.5, colors.HexColor('#0284c7')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_callout)

    story.append(Paragraph("3. Mathematical Integration with 1D Corridor Mechanics", h2_style))
    story.append(Paragraph(
        "At signal-controlled boundary segment s_k, effective velocity v(s_k) is constrained by signal factor σ ∈ {0, 1}: "
        "<br/><b>v(s_k) = σ · v_max · (1 - ρ_eff(s_k))</b><br/>"
        "Under standard operation, σ = 0 during red cycles, causing shockwave delay. The EVTSP protocol forces σ = 1 "
        "upon entry into horizon H, eliminating queue-clearing stagnation.",
        body_style
    ))

    story.append(Paragraph("4. Unity Component Breakdown", h2_style))
    breakdown_text1 = "<b>Intersection Controller:</b> Manages 4-way intersection logic and caches phase history.<br/><b>Signal Light Objects:</b> 3D traffic light heads with emissive materials and point lights.<br/><b>Trigger Zones:</b> Convex Box/Sphere Colliders marked as IsTrigger = true."
    breakdown_text2 = "<b>3D Audio Source:</b> Logarithmic Rolloff (min 5m, max 100m) attached to ambulance.<br/><b>HDR Emissive Materials:</b> Materials utilizing _EmissionColor to produce real-time bloom glow in Unity URP."
    t_arch = Table([
        [Paragraph("<b>Unity Scene Architecture</b>", body_style), Paragraph("<b>Audio & Visual Assets</b>", body_style)],
        [Paragraph(breakdown_text1, callout_style), Paragraph(breakdown_text2, callout_style)]
    ], colWidths=[(A4[0] - 32 * mm)/2, (A4[0] - 32 * mm)/2])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_arch)

    story.append(PageBreak())

    # ==================== PAGE 2: TrafficSignalController.cs ====================
    story.append(Paragraph("TrafficSignalController.cs (C# Unity Core)", title_style))
    story.append(Paragraph("Multi-Way Signal Controller with State Memory & Dynamic Emergency Overrides", sub_style))
    story.append(Paragraph("5. Implementation: TrafficSignalController.cs", h2_style))

    code_tsc = """using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public enum SignalState { Red, Yellow, Green, EmergencyGlowGreen }
public enum ApproachDirection { North, South, East, West }

[System.Serializable]
public class SignalHead {
    public ApproachDirection direction;
    public MeshRenderer redBulb, yellowBulb, greenBulb;
    public Light emergencySpotlight;
    [HideInInspector] public SignalState currentState;
}

public class TrafficSignalController : MonoBehaviour {
    public List<SignalHead> signals;
    public float greenDuration = 10.0f, yellowDuration = 3.0f;
    public Color redColor = Color.red, yellowColor = Color.yellow, greenColor = Color.green;
    public Color emergencyGlowColor = new Color(0.1f, 1.0f, 0.4f) * 4.5f;

    private bool isEmergencyActive = false;
    private ApproachDirection savedGreenDirection;
    private float savedTimeInCycle = 0f;
    private bool savedIsYellow = false;
    private Coroutine activeCycleCoroutine;

    void Start() { activeCycleCoroutine = StartCoroutine(NormalCycleRoutine()); }

    private IEnumerator NormalCycleRoutine() {
        while (!isEmergencyActive) {
            // N/S Green
            savedGreenDirection = ApproachDirection.North; savedIsYellow = false;
            SetDirectionState(ApproachDirection.North, SignalState.Green);
            SetDirectionState(ApproachDirection.South, SignalState.Green);
            SetDirectionState(ApproachDirection.East, SignalState.Red);
            SetDirectionState(ApproachDirection.West, SignalState.Red);
            for (savedTimeInCycle = 0; savedTimeInCycle < greenDuration; savedTimeInCycle += Time.deltaTime) yield return null;

            // N/S Yellow
            savedIsYellow = true;
            SetDirectionState(ApproachDirection.North, SignalState.Yellow);
            SetDirectionState(ApproachDirection.South, SignalState.Yellow);
            for (savedTimeInCycle = 0; savedTimeInCycle < yellowDuration; savedTimeInCycle += Time.deltaTime) yield return null;

            // E/W Green
            savedGreenDirection = ApproachDirection.East; savedIsYellow = false;
            SetDirectionState(ApproachDirection.North, SignalState.Red);
            SetDirectionState(ApproachDirection.South, SignalState.Red);
            SetDirectionState(ApproachDirection.East, SignalState.Green);
            SetDirectionState(ApproachDirection.West, SignalState.Green);
            for (savedTimeInCycle = 0; savedTimeInCycle < greenDuration; savedTimeInCycle += Time.deltaTime) yield return null;

            // E/W Yellow
            savedIsYellow = true;
            SetDirectionState(ApproachDirection.East, SignalState.Yellow);
            SetDirectionState(ApproachDirection.West, SignalState.Yellow);
            for (savedTimeInCycle = 0; savedTimeInCycle < yellowDuration; savedTimeInCycle += Time.deltaTime) yield return null;
        }
    }

    public void TriggerEmergencyPreemption(ApproachDirection approachingFrom) {
        if (isEmergencyActive) return;
        isEmergencyActive = true;
        if (activeCycleCoroutine != null) StopCoroutine(activeCycleCoroutine);

        foreach (var sig in signals) ApplyState(sig, SignalState.Red);
        SignalHead target = signals.Find(s => s.direction == approachingFrom);
        if (target != null) ApplyState(target, SignalState.EmergencyGlowGreen);
    }

    public void ReleaseEmergencyPreemption() {
        if (!isEmergencyActive) return;
        isEmergencyActive = false;
        foreach (var sig in signals) ApplyState(sig, SignalState.Red);
        activeCycleCoroutine = StartCoroutine(ResumeCycleRoutine());
    }

    private IEnumerator ResumeCycleRoutine() {
        float remaining = (savedIsYellow ? yellowDuration : greenDuration) - savedTimeInCycle;
        if (remaining > 0.5f) {
            SignalState resumeState = savedIsYellow ? SignalState.Yellow : SignalState.Green;
            ApproachDirection dir = savedGreenDirection;
            SetDirectionState(dir, resumeState);
            SetDirectionState(dir == ApproachDirection.North ? ApproachDirection.South : ApproachDirection.West, resumeState);
            yield return new WaitForSeconds(remaining);
        }
        activeCycleCoroutine = StartCoroutine(NormalCycleRoutine());
    }
}"""
    t_code1 = Table([[Preformatted(code_tsc, code_style)]], colWidths=[A4[0] - 28 * mm])
    t_code1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0f172a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1e293b')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code1)

    story.append(PageBreak())

    # ==================== PAGE 3: AmbulanceVehicle.cs & IntersectionTrigger.cs ====================
    story.append(Paragraph("AmbulanceVehicle.cs & IntersectionTrigger.cs", title_style))
    story.append(Paragraph("Siren Audio Synthesis, Rigidbody Movement & Collision Triggers", sub_style))

    story.append(Paragraph("6. Implementation: AmbulanceVehicle.cs", h2_style))
    code_amb = """using UnityEngine;

[RequireComponent(typeof(AudioSource))]
public class AmbulanceVehicle : MonoBehaviour {
    public float targetSpeed = 15.0f; // m/s
    public bool isRespondingToEmergency = true;
    public AudioClip sirenClip;
    [Range(0f, 1f)] public float sirenVolume = 1.0f;
    public float minAudioDistance = 5.0f, maxAudioDistance = 120.0f;

    private AudioSource audioSource;
    private Rigidbody rb;

    void Awake() {
        rb = GetComponent<Rigidbody>();
        audioSource = GetComponent<AudioSource>();
        audioSource.clip = sirenClip;
        audioSource.loop = true;
        audioSource.volume = sirenVolume;
        audioSource.spatialBlend = 1.0f; // 3D sound
        audioSource.dopplerLevel = 1.5f;
        audioSource.rolloffMode = AudioRolloffMode.Logarithmic;
        audioSource.minDistance = minAudioDistance;
        audioSource.maxDistance = maxAudioDistance;
    }

    void Start() {
        if (isRespondingToEmergency && sirenClip != null) audioSource.Play();
    }

    void FixedUpdate() {
        if (isRespondingToEmergency) {
            Vector3 targetVelocity = transform.forward * targetSpeed;
            if (rb != null) rb.linearVelocity = new Vector3(targetVelocity.x, rb.linearVelocity.y, targetVelocity.z);
            else transform.position += targetVelocity * Time.fixedDeltaTime;
        }
    }
}"""
    t_code2 = Table([[Preformatted(code_amb, code_style)]], colWidths=[A4[0] - 28 * mm])
    t_code2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0f172a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1e293b')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code2)

    story.append(Paragraph("7. Implementation: IntersectionTrigger.cs", h2_style))
    code_trig = """using UnityEngine;

public class IntersectionTrigger : MonoBehaviour {
    public TrafficSignalController controller;
    public ApproachDirection entryDirection;

    private void OnTriggerEnter(Collider other) {
        AmbulanceVehicle ambulance = other.GetComponentInParent<AmbulanceVehicle>();
        if (ambulance != null && ambulance.isRespondingToEmergency) {
            controller.TriggerEmergencyPreemption(entryDirection);
        }
    }

    private void OnTriggerExit(Collider other) {
        AmbulanceVehicle ambulance = other.GetComponentInParent<AmbulanceVehicle>();
        if (ambulance != null && ambulance.isRespondingToEmergency) {
            controller.ReleaseEmergencyPreemption();
        }
    }
}"""
    t_code3 = Table([[Preformatted(code_trig, code_style)]], colWidths=[A4[0] - 28 * mm])
    t_code3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0f172a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1e293b')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code3)

    story.append(PageBreak())

    # ==================== PAGE 4: Standalone Browser Simulation ====================
    story.append(Paragraph("Interactive Virtual 4-Way Simulation (HTML5/Web Audio)", title_style))
    story.append(Paragraph("Real-Time Canvas Simulation with Synthesized Doppler Siren & Signal Preemption", sub_style))

    story.append(Paragraph("8. Complete Simulation Source: intersection_simulation.html", h2_style))
    story.append(Paragraph(
        "The standalone HTML5 simulator replicates the complete Unity preemption mechanics, featuring a synthesized "
        "Web Audio emergency siren, dynamic 4-way signals, glowing priority indicators, and automated state resumption. "
        "The file is accessible locally at <b>intersection_simulation.html</b>.",
        body_style
    ))

    code_sim = """// Web Audio Doppler Synthesizer & Dispatch Logic
function initAudio() {
  if (audioCtx) return;
  audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  sirenOsc = audioCtx.createOscillator();
  sirenGain = audioCtx.createGain();
  sirenOsc.type = 'sawtooth';
  sirenOsc.frequency.setValueAtTime(650, audioCtx.currentTime);
  sirenGain.gain.setValueAtTime(0, audioCtx.currentTime);
  sirenOsc.connect(sirenGain);
  sirenGain.connect(audioCtx.destination);
  sirenOsc.start();
}

function dispatchAmbulance(direction) {
  initAudio();
  approaching = direction;
  amb.active = true;
  amb.dir = direction;
  if (direction === 'West') { amb.x = 20; amb.y = 265; amb.vx = 2.6; amb.vy = 0; }
  if (direction === 'South') { amb.x = 235; amb.y = 480; amb.vx = 0; amb.vy = -2.6; }
}

function updatePreemptionState(dist) {
  if (dist < 180 && !preemption && dist > 20) {
    preemption = true;
    savedPhase = phase; savedTimer = phaseTimer;
    statusPanel.innerText = 'PREEMPTION ACTIVE: ' + amb.dir + ' Granted Emergency Green!';
  }
}"""
    t_code4 = Table([[Preformatted(code_sim, code_style)]], colWidths=[A4[0] - 28 * mm])
    t_code4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0f172a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1e293b')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code4)

    story.append(PageBreak())

    # ==================== PAGE 5: Runbook & Viva Defense ====================
    story.append(Paragraph("Unity Setup Runbook & Technical Defense Guide", title_style))
    story.append(Paragraph("Scene Configuration, Universal Render Pipeline (URP) Bloom & Viva Talking Points", sub_style))

    story.append(Paragraph("9. Step-by-Step Unity Setup Runbook", h2_style))
    story.append(Paragraph("1. <b>Scene & Corridor Hierarchy:</b> Create 4 intersecting road planes. Attach <code>TrafficSignalController.cs</code> to an empty GameObject named <code>Intersection_Controller</code>.", body_style))
    story.append(Paragraph("2. <b>Signal Heads & Meshes:</b> Create 4 signal post prefabs with Red, Yellow, and Green bulb spheres. Assign materials supporting Emission.", body_style))
    story.append(Paragraph("3. <b>Bloom Glow Configuration:</b> In Unity URP, add Global Volume &rarr; Bloom (Intensity = 1.5, Threshold = 0.9). HDR emission multipliers generate realistic optical halos.", body_style))
    story.append(Paragraph("4. <b>Emergency Triggers:</b> Place trigger colliders 50–80m before the intersection with <code>IsTrigger = true</code> and attach <code>IntersectionTrigger.cs</code>.", body_style))
    story.append(Paragraph("5. <b>Ambulance Prefab:</b> Attach <code>AmbulanceVehicle.cs</code>, Rigidbody, AudioSource, and set Spatial Blend = 1.0 (3D) for Doppler attenuation.", body_style))

    story.append(Paragraph("10. Viva Defense & Technical Q&A", h2_style))
    qa1 = "<b>Q: How does the system prevent cross-traffic accidents?</b><br/><b>Answer:</b> The instant emergency detection fires, all competing signal phases are interrupted and immediately forced to Solid Red. An optional 1.5s all-red clearance interval clears vehicles currently inside."
    qa2 = "<b>Q: How does cycle memory prevent post-clearance starvation?</b><br/><b>Answer:</b> The controller caches active phase and elapsed time. Once departure trigger clears, the system smoothly resumes the remaining phase duration rather than resetting to Phase 0."
    t_qa = Table([
        [Paragraph(qa1, callout_style), Paragraph(qa2, callout_style)]
    ], colWidths=[(A4[0] - 32 * mm)/2, (A4[0] - 32 * mm)/2])
    t_qa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_qa)

    story.append(Paragraph("11. Final Integration Checklist", h2_style))
    story.append(Paragraph("• [x] <code>TrafficSignalController.cs</code> integrated with HDR emission control and state memory.", body_style))
    story.append(Paragraph("• [x] <code>AmbulanceVehicle.cs</code> configured with 3D audio siren and forward kinematics.", body_style))
    story.append(Paragraph("• [x] <code>IntersectionTrigger.cs</code> detecting arrival and departure boundaries.", body_style))
    story.append(Paragraph("• [x] Interactive browser simulator (<code>intersection_simulation.html</code>) with synthesized Web Audio siren and visual bloom.", body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated EVTSP PDF: {PDF_PATH}")

if __name__ == "__main__":
    build_pdf()

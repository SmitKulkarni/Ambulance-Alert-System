using UnityEngine;

[RequireComponent(typeof(AudioSource))]
public class AmbulanceVehicle : MonoBehaviour
{
    [Header("Kinematics")]
    public float targetSpeed = 15.0f; // m/s
    public bool isRespondingToEmergency = true;

    [Header("Audio Siren Configuration")]
    public AudioClip sirenClip;
    [Range(0f, 1f)] public float sirenVolume = 1.0f;
    public float minAudioDistance = 5.0f;
    public float maxAudioDistance = 120.0f;

    private AudioSource audioSource;
    private Rigidbody rb;

    void Awake()
    {
        rb = GetComponent<Rigidbody>();
        audioSource = GetComponent<AudioSource>();

        // Configure 3D Spatial Audio and Doppler Effect
        audioSource.clip = sirenClip;
        audioSource.loop = true;
        audioSource.volume = sirenVolume;
        audioSource.spatialBlend = 1.0f; // Fully 3D sound
        audioSource.dopplerLevel = 1.5f;
        audioSource.rolloffMode = AudioRolloffMode.Logarithmic;
        audioSource.minDistance = minAudioDistance;
        audioSource.maxDistance = maxAudioDistance;
    }

    void Start()
    {
        if (isRespondingToEmergency && sirenClip != null)
        {
            audioSource.Play();
        }
    }

    void FixedUpdate()
    {
        if (isRespondingToEmergency)
        {
            // Continuous forward displacement along local heading
            Vector3 targetVelocity = transform.forward * targetSpeed;
            if (rb != null)
                rb.linearVelocity = new Vector3(targetVelocity.x, rb.linearVelocity.y, targetVelocity.z);
            else
                transform.position += targetVelocity * Time.fixedDeltaTime;
        }
    }
}

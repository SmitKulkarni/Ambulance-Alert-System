using UnityEngine;

public class IntersectionTrigger : MonoBehaviour
{
    public TrafficSignalController controller;
    public ApproachDirection entryDirection;

    private void OnTriggerEnter(Collider other)
    {
        AmbulanceVehicle ambulance = other.GetComponentInParent<AmbulanceVehicle>();
        if (ambulance != null && ambulance.isRespondingToEmergency)
        {
            // Request exclusive priority for this approach
            controller.TriggerEmergencyPreemption(entryDirection);
        }
    }

    private void OnTriggerExit(Collider other)
    {
        AmbulanceVehicle ambulance = other.GetComponentInParent<AmbulanceVehicle>();
        if (ambulance != null && ambulance.isRespondingToEmergency)
        {
            // Release priority: ambulance has cleared the intersection, restore previous cycle
            controller.ReleaseEmergencyPreemption();
        }
    }
}

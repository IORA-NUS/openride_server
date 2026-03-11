from flask import request, jsonify, Blueprint
from flask import current_app as app
from api.config import settings

blueprint = Blueprint('admin', __name__, url_prefix='/admin')


from api.utils import plot_state_machine
from api.state_machine import (RidehailDriverTripStateMachine,
                    RidehailPassengerTripStateMachine,
                    WorkflowStateMachine,
                    UserStateMachine,
                    HLDeliveryDriverTourStateMachine,
                    HLDeliveryPackageTripStateMachine)

# from api.models import (
#     UserStates,
#     WorkflowStates,
#     # DriverTripStates,
#     PassengerTripStates
# )

@blueprint.route('/plot_state_machines', methods=['POST'])
def state_machine_plotter():
    """
    Generates and plots state diagrams for multiple state machine classes.

    This function iterates over a predefined list of state machine classes and calls
    `plot_state_machine` for each, generating their respective state diagrams. Upon completion,
    returns a JSON response indicating success.

    Returns:
        tuple: A JSON response with the message 'Success' and HTTP status code 200.
    """
    for sm in [UserStateMachine,
            WorkflowStateMachine,
            RidehailDriverTripStateMachine,
            RidehailPassengerTripStateMachine,
            HLDeliveryDriverTourStateMachine,
            HLDeliveryPackageTripStateMachine]:
        plot_state_machine(sm)

    return jsonify('Success'), 200

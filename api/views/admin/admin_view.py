from flask import request, jsonify, Blueprint
from flask import current_app as app
from api.config import settings

blueprint = Blueprint('admin', __name__, url_prefix='/admin')


from api.utils import plot_state_machine
from api.lib import (RidehailDriverTripStateMachine,
                    RidehailPassengerTripStateMachine,
                    WorkflowStateMachine,
                    UserStateMachine,
                    DeliveryDriverTourStateMachine,
                    DeliveryPackageTripStateMachine)

# from api.models import (
#     UserStates,
#     WorkflowStates,
#     # DriverTripStates,
#     PassengerTripStates
# )

@blueprint.route('/plot_state_machines', methods=['POST'])
def state_machine_plotter():
    for sm in [UserStateMachine,
            WorkflowStateMachine,
            RidehailDriverTripStateMachine,
            RidehailPassengerTripStateMachine,
            DeliveryDriverTourStateMachine,
            DeliveryPackageTripStateMachine]:
        plot_state_machine(sm)

    return jsonify('Success'), 200

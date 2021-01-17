from fittrackee.responses import HttpResponse
from fittrackee.users.models import User
from fittrackee.workouts.models import Workout
from flask import Blueprint, current_app

from .utils import federation_required

ap_nodeinfo_blueprint = Blueprint('ap_nodeinfo', __name__)


@ap_nodeinfo_blueprint.route('/.well-known/nodeinfo', methods=['GET'])
@federation_required
def get_nodeinfo_url() -> HttpResponse:
    nodeinfo_url = f'https://{current_app.config["AP_DOMAIN"]}/nodeinfo/2.0'
    response = {
        'links': [
            {
                'rel': 'http://nodeinfo.diaspora.software/ns/schema/2.0',
                'href': nodeinfo_url,
            }
        ]
    }
    return HttpResponse(
        response=response, content_type='application/json; charset=utf-8'
    )


@ap_nodeinfo_blueprint.route('/nodeinfo/2.0', methods=['GET'])
@federation_required
def get_nodeinfo() -> HttpResponse:
    # TODO : add 'activeHalfyear' and 'activeMonth' for users
    workouts_count = Workout.query.filter().count()
    users_count = User.query.filter().count()
    response = {
        'version': '2.0',
        'software': {
            'name': 'fittrackee',
            'version': current_app.config['VERSION'],
        },
        'protocols': ['activitypub'],
        'usage': {
            'users': {'total': users_count},
            'localWorkouts': workouts_count,
        },
        'openRegistrations': current_app.config['is_registration_enabled'],
    }
    return HttpResponse(
        response=response, content_type='application/json; charset=utf-8'
    )
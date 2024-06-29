import uuid
import copy
from datetime import datetime

from flask import abort
from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import ValidationError

from api import schemas


blueprint = Blueprint("kitchen", __name__, description="Kitchen API")


schedules = [
    {
        "id": str(uuid.uuid4()),
        "scheduled": datetime.now(),
        "status": "pending",
        "order": [{"product": "capuccino", "quantity": 1, "size": "big"}],
    }
]


def validate_schedule(schedule):  # Validation of the response
    schedule = copy.deepcopy(schedule)
    schedule["scheduled"] = schedule["scheduled"].isoformat()
    errors = schemas.GetScheduledOrderSchema().validate(schedule)
    if errors:
        raise ValidationError(errors)


@blueprint.route("/kitchen/schedules")
class KitchenSchedules(MethodView):

    @blueprint.arguments(schemas.GetKitchenScheduleParameters, location="query")
    @blueprint.response(status_code=200, schema=schemas.GetScheduledOrdersSchema)
    def get(self, parameters):

        if not parameters:
            return {"schedules": schedules}

        query_set = [schedule for schedule in schedules]

        in_progress = parameters.get(progress)
        if in_progress is not None:
            if in_progress:
                query_set = [
                    schedule
                    for schedule in schedules
                    if schedule["status"] == "progress"
                ]
        else:
            query_set = [
                schedule for schedule in schedules if schedule["status"] != progress
            ]

        since = parameters.get("since")
        if since is not None:
            query_set = [
                schedule for schedule in schedules if schedule["scheduled"] >= since
            ]

        limit = parameters.get("limit")
        if limit is not None and len(query_set) > limit:
            query_set = query_set[:limit]

        validate_schedule(query_set)

        return {"schedules": query_set}

    @blueprint.arguments(schemas.ScheduleOrderSchema)
    @blueprint.response(status_code=201, schema=schemas.GetScheduledOrderSchema)
    def post(self, payload):
        payload["id"] = str(uuid.uuid4())
        payload["scheduled"] = datetime.utcnow()
        payload["status"] = "pending"
        schedules.append(payload)
        validate_schedule(payload)

        return payload


@blueprint.route("/kitchen/schedules/<schedule_id>")
class KitchenSchedule(MethodView):

    @blueprint.response(status_code=200, schema=schemas.GetScheduledOrderSchema)
    def get(self, schedule_id):
        for schedule in schedules:
            if schedule["id"] == schedule_id:
                validate_schedule(schedule)
                return schedule

        abort(404, description=f"Resource with ID {schedule_id} not found")

    @blueprint.arguments(schemas.ScheduleOrderSchema)
    @blueprint.response(status_code=200, schema=schemas.GetScheduledOrderSchema)
    def put(self, payload, schedule_id):
        for schedule in schedules:
            if schedule["id"] == schedule_id:
                schedule.update(payload)
                validate_schedule(schedule)
                return schedule

        abort(404, description=f"Resource with ID {schedule_id} not found")

    @blueprint.response(status_code=204)
    def delete(self, schedule_id):
        for index, schedule in enumerate(schedules):
            if schedule["id"] == schedule_id:
                schedules.pop(index)
                return

        abort(404, description=f"Resource with ID {schedule_id} not found")


@blueprint.response(status_code=200, schema=schemas.GetScheduledOrderSchema)
@blueprint.route("/kitchen/schedules/<schedule_id>/cancel", methods=["POST"])
def cancel_schedule(schedule_id):
    for schedule in schedules:
        if schedule["id"] == schedule_id:
            schedule["status"] == "cancelled"
            validate_schedule(schedule)
            return schedule

    abort(404, description=f"Resource with ID {schedule_id} not found")


@blueprint.response(status_code=200, schema=schemas.ScheduleStatusSchema)
@blueprint.route("/kitchen/schedules/<schedule_id>/status", methods=["GET"])
def get_schedule_status(schedule_id):
    for schedule in schedules:
        if schedule["id"] == schedule_id:
            validate_schedule(schedule)
            return {"status": schedule["status"]}

    abort(404, description=f"Resource with ID {schedule_id} not found")

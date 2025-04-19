from anmelde_tool.registration.models import Registration, RegistrationParticipant
from anmelde_tool.event import models as event_models

# class RegistrationEventKPISerializer(serializers.ModelSerializer):
#     scout_organisation = basic_serializers.ScoutHierarchyDetailedSerializer(many=False, read_only=True)
#     count = serializers.IntegerField()

#     class Meta:
#         model = Registration
#         fields = (
#             'scout_organisation',
#             'created_at',
#             'updated_at',
#             'count'
#         )

# class BookingOptionKPISerializer(serializers.ModelSerializer):
#     value = serializers.SerializerMethodField()
#     class Meta:
#         model = event_models.BookingOption
#         fields = (
#             'name',
#             'price',
#             'value'
#         )
        
#     def get_value(self, obj: event_models.BookingOption) -> str:
#         return RegistrationParticipant.objects \
#             .filter(booking_option=obj.id).count()

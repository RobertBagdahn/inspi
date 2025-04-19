import math
from zipfile import ZipFile

from django.db.models import QuerySet
from openpyxl import load_workbook, Workbook
from openpyxl.drawing import image

from anmelde_tool.event.file_generator.generators import helper
from anmelde_tool.event.file_generator.generators.abstract_generator import AbstractGenerator
from anmelde_tool.event.file_generator.models import FileTemplate
from anmelde_tool.event.basic.models import Event
from anmelde_tool.registration.models import Registration, RegistrationParticipant


class KjpGeneratorV2(AbstractGenerator):

    def generate(self) -> Workbook:
        event: Event = self.generated_file.event
        registrations: QuerySet[Registration] = helper.get_registrations(event)

        file: FileTemplate = self.generated_file.template
        wb: Workbook = load_workbook(file.file)

        original = wb.get_sheet_by_name('Vorlage')
        anchor = original._images[0].anchor

        zip = ZipFile(file.file)
        zip.extractall()

        sheets_count = 0
        max_sheet_count = 0
        participants_count = 0
        registration: Registration

        bund_name = helper.get_bund_name(self.generated_file)

        current_year = helper.get_current_year()

        for registration in registrations:
            max_sheet_count += math.ceil(registration.registrationparticipant_set.count() / 10)


        for registration in registrations:
            participants = registration.registrationparticipant_set.all().order_by('last_name')
            participant_count = participants.count()
            registration_index:int
            chunked_registration_indices: int
            for registration_index, chunked_registration_indices in enumerate(range(0, participant_count, 10)):
                registration_chunk = participants[chunked_registration_indices:chunked_registration_indices + 10]
                sheet = wb.copy_worksheet(original)
                sheets_count += 1
                registration_sheet_num = registration_index+ 1
                sheet.title = f'{registration.scout_organisation.name.strip()}_{registration_sheet_num}'

                logo = image.Image('xl/media/image1.png')
                logo.anchor = anchor
                sheet.add_image(logo)

                sheet['R11'] = event.name
                sheet['AC11'] = helper.get_event_location(event)
                sheet['AJ11'] = helper.get_event_date(event)
                sheet['AO11'] = helper.get_event_days(event)
                sheet['AP3'] = sheets_count
                sheet['AR3'] = max_sheet_count
                sheet['M1'] = current_year
                sheet['F8'] = bund_name


                participant: RegistrationParticipant
                for participant_index, participant in enumerate(registration_chunk):
                    cell = participant_index * 2 + 19
                    participants_count += 1
                    sheet[f'A{cell}'] = participants_count
                    sheet[f'C{cell}'] = f'{helper.get_participant_full_name(participant)}' \
                                        f'\n{helper.get_participant_adress(participant)}'
                    sheet[f'P{cell}'] = helper.get_participant_gender(participant)
                    sheet[f'R{cell}'] = helper.get_participant_state(participant)
                    sheet[f'U{cell}'] = helper.get_participant_below_27(event, participant)
                    sheet[f'AQ{cell}'] = helper.get_participant_days(event, participant)

        if len(wb.worksheets) > 1:
            wb.remove(original)
        return wb

import os
import time

from xlwt import Workbook

from resources.utils import UPLOAD_FOLDER


def export_to_excel(objects, id):
    wb = Workbook()
    sheet = wb.add_sheet('Sheet 1')

    i = 1
    fields = []
    sheet.write(0, 0, 'Sr No')

    for field in objects.first()._fields:
        fields.append(field)
        sheet.write(0, i, field)
        i += 1

    j = 1
    for obj in objects:
        n = 1
        sheet.write(j, 0, str(j))
        for m in fields:
            val = getattr(obj, m)
            if val is not None:
                sheet.write(j, n, str(val))
            n += 1
        j += 1

    filename = id + "_" + time.strftime("%Y%m%d-%H%M%S")
    file = os.path.join(UPLOAD_FOLDER, filename)
    wb.save(f"{file}.xls")
    return filename + ".xls"

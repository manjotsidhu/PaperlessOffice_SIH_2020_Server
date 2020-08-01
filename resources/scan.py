import json
import os
import time

from flask import request, send_from_directory
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from resources.utils import UPLOAD_FOLDER, allowed_file, get_file_extension
from services.scanner.scanning import scan


class ScanApi(Resource):
    @jwt_required
    def post(self):
        if 'file' not in request.files:
            return {'No File Sent'}, 404
        file = request.files['file']
        if file.filename == '':
            return {'No File Selected'}, 404
        if file:
            body = request.form.to_dict()

            fileExtension = None
            if 'fileExt' in body:
                fileExtension = body['fileExt']
            else:
                fileExtension = get_file_extension(file.filename)

            fileName = get_jwt_identity()['_id']['$oid'] + "_" + time.strftime(
                "%Y%m%d-%H%M%S")

            input = os.path.join(UPLOAD_FOLDER, fileName + "." + fileExtension)
            output = os.path.join(UPLOAD_FOLDER, fileName + "_scanned." + fileExtension)
            file.save(input)

            scan(input, output)
            return send_from_directory(directory=UPLOAD_FOLDER, filename=fileName + "_scanned." + fileExtension)

        else:
            return {'Error: Invalid Document'}, 405
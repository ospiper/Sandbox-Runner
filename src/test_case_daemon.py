import os
import shutil
import uuid

from flask import Flask, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
import zipfile

from config import TEST_CASE_DIR

ALLOWED_EXTENSIONS = {'zip'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['TEST_CASE_DIR'] = TEST_CASE_DIR
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024


def unzip(src_file, dest_dir):
    zf = zipfile.ZipFile(src_file)
    try:
        zf.extractall(path=dest_dir)
    except RuntimeError as e:
        print(e)
    zf.close()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        problem_id = str(filename.split('/')[-1]).split('.')[0]
        zip_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        case_path = os.path.join(app.config['TEST_CASE_DIR'], problem_id)
        while os.path.exists(case_path):
            problem_id = str(uuid.uuid4())
            case_path = os.path.join(app.config['TEST_CASE_DIR'], problem_id)
        os.makedirs(case_path)
        file.save(zip_filename)
        unzip(zip_filename, case_path)
        os.remove(zip_filename)
        print('Problem %s created' % problem_id)
        return problem_id


@app.route('/clean_up', methods=['POST'])
def clean_up():
    problem_id = request.form['problem_id']
    if problem_id:
        print('Removing problem %s' % problem_id)
        case_path = os.path.join(app.config['TEST_CASE_DIR'], problem_id)
        print(case_path)
        if os.path.exists(case_path):
            shutil.rmtree(case_path)
    return ''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

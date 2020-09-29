# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from uuid import uuid4
from time import sleep
from google.cloud import aiplatform as aip

from samples import (
    create_data_labeling_job_sample,
    cancel_data_labeling_job_sample,
    delete_data_labeling_job_sample,
)

PROJECT_ID = "ucaip-sample-tests"
LOCATION = "us-central1"
DATASET_ID = "1905673553261363200"  # AUTOPUSH: Permanent no label dataset
DISPLAY_NAME = f"temp_create_data_labeling_job_test_{uuid4()}"
INPUTS_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/datalabelingjob/inputs/image_classification.yaml"
INSTRUCTIONS_GCS_URI = (
    "gs://ucaip-sample-resources/images/datalabeling_instructions.pdf"
)
ANNOTATION_SPEC = "daisy"


DATA_LABELING_JOB_NAME = None


@pytest.fixture(scope="function", autouse=True)
def teardown(capsys):
    yield

    assert DATA_LABELING_JOB_NAME is not None

    data_labeling_job_id = DATA_LABELING_JOB_NAME.split("/")[-1]
    
    client_options = dict(
        api_endpoint="us-central1-autopush-aiplatform.sandbox.googleapis.com"
    )
    client = aip.JobServiceClient(client_options=client_options)
    
    name = client.data_labeling_job_path(
        project=PROJECT_ID, location=LOCATION, data_labeling_job=data_labeling_job_id
    )
    client.cancel_data_labeling_job(name=name)

    # Verify Data Labelling Job is cancelled, or timeout after 400 seconds
    for i in range(40):
        response = client.get_data_labeling_job(name=name)
        if "CANCELLED" in str(response.state):
            break
        sleep(10)

    # Delete the data labeling job
    response = client.delete_data_labeling_job(name=name)
    print("Delete LRO:", response.operation.name)
    delete_data_labeling_job_response = response.result(timeout=300)
    print("delete_data_labeling_job_response", delete_data_labeling_job_response)

    out, _ = capsys.readouterr()
    assert "delete_data_labeling_job_response" in out


# Creating a data labeling job for images
def test_ucaip_generated_create_data_labeling_job_sample(capsys):
    global DATA_LABELING_JOB_NAME
    assert DATA_LABELING_JOB_NAME is None

    dataset_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/datasets/{DATASET_ID}"

    create_data_labeling_job_sample.create_data_labeling_job_sample(
        project=PROJECT_ID,
        display_name=DISPLAY_NAME,
        instruction_uri=INSTRUCTIONS_GCS_URI,
        dataset_name=dataset_name,
        inputs_schema_uri=INPUTS_SCHEMA_URI,
        annotation_spec=ANNOTATION_SPEC,
    )

    out, _ = capsys.readouterr()

    # Save resource name of the newly created data labeing job
    DATA_LABELING_JOB_NAME = out.split("name:")[1].split("\n")[0]
#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""

    Scripts that uploads all the apk files found in current or argument passed folder to the beta
    track.

    USAGE: python multiapk_upload.py ../archive/V20161122

    (remember to be in the same folder as the script before running)

"""

import argparse
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client import client
from apiclient.discovery import build
import os  

TRACK = 'beta'  # Can be 'alpha', beta', 'production' or 'rollout'

APP_PACKAGE = 'YOUR APP PACKAGE ID'

SERVICE_ACCOUNT_EMAIL = (
    'YOUR SERVICE @ EMAIL ADDRESS HERE')

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
# argparser.add_argument('package_name', nargs='?', default='com.peerwell',
#                        help='The package name. Example: com.android.sample')
argparser.add_argument('apks_folder',
                       nargs='?',
                       default='.',
                       help='Folder containing APK files to upload.')


def main():

  key='key.json'

  scopes = ['https://www.googleapis.com/auth/androidpublisher']

  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      key,
      scopes)
  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build('androidpublisher', 'v2', http=http)

  # Process flags and read their values.
  flags = argparser.parse_args()
  package_name = APP_PACKAGE #flags.package_name
  apks_folder = flags.apks_folder
  apks = []
  apkResponses = []

  try:

    for apk_file in os.listdir(apks_folder):
      if os.path.isfile(apks_folder + "/" + apk_file) and ".apk" in apk_file:
        apks.append(apks_folder + "/" + apk_file)

    if (apks == []):
      print "Error. No apk files found"
      return

    print apks

    edit_request = service.edits().insert(body={}, packageName=package_name)
    result = edit_request.execute()
    edit_id = result['id']
    print "edit_id: ", edit_id

    for apk_file in apks:
      if not "universal" in apk_file:
        print "uploading: ", apk_file

        # continue
        apk_response = service.edits().apks().upload(
            editId=edit_id,
            packageName=package_name,
            media_body=apk_file).execute()

        print 'Version code %d has been uploaded' % apk_response['versionCode']
        apkResponses.append(apk_response['versionCode'])

    track_response = service.edits().tracks().update(
        editId=edit_id,
        track=TRACK,
        packageName=package_name,
        body={u'versionCodes': apkResponses}).execute()

    print 'Track %s is set for version code(s) %s' % (
    track_response['track'], str(track_response['versionCodes']))

    commit_request = service.edits().commit(
        editId=edit_id, packageName=package_name).execute()

    print 'Edit "%s" has been committed' % (commit_request['id'])

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main()

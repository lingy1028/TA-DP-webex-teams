# Webex Teams Modular Input

Authors: Datapunctum GmbH
Description: Webex Teams Modular Input
Version: 1.0.3

## Introduction

The purpose of this add-on is to collect Webex Teams Events and Webex Teams Audit-Events through the [Webex Teams API](https://developer.webex.com/docs/api/getting-started)

This Add-on has been built using the Splunk Add-on Builder

## Special Features

* If files have been uploaded in a message, the event can be enriched with file information.
* If rooms have been created, the event can be enriched with the room title.
* Messages can be masked for privacy

## Authentication

Authentication to the API is through Personal Access Tokens. An Personal Access Token can be acquired through a Refresh Token, which has to be renewed once a while.
##### v1.0.1
The Add-on expects an active Refresh Tokens and keeps track of the lifetime of the Access Token and automatically refreshes the access token if needed.

Additionally to the Refresh Token, the Client ID and Client Secret has to be provided.

Multiple Refresh Tokens with different access rights.(up to 4) may be configured and referenced by Inputs.

##### v.1.0.3
In this version, the Add-on integrates the OAuth flow to get the Access Token and a Refresh Token in the configuration phase, and keeps track of the lifetime of the Access Token and automatically refreshes the access token if needed.

#### Create a Webex Teams OAuth Integration App

An integration is what you'd have to use if you have Single Sign-On (SSO) or OAuth enabled in your Webex account and you are not able to create a Service Account. 
- Log in to [Cisco Webex for Developers](https://developer.webex.com/my-apps/new/integration) using a Webex Account with `compliance officer` Role.
(This Add-on will hit the Webex teams’s Events API endpoint, which requires the `Spark-compliance:events_read` scope. In order to use the `Spark-compliance:events_read` scope you need to be a designated `compliance officer` for your organization in Webex Control Hub. Please make sure the account you used to create this integration has been assigned this role. You can assign this role to a user in [Webex Control Hub](https://admin.webex.com/).)

- Enter the following details:
    - **Integration name**: Enter a integration name as you like. 
    - **Contact email**: Enter a contact email address.
    - **Icon**: Select a default Icon
    - **Description**: Write a description of your integration
    - **Redirect URI**: The Redirect URI **MUST** follow this pattern:

    ```https://{{hostname}}/en-US/splunkd/__raw/services/webex-teams-oauth```

    Please replace the `{{hostname}}` with the hostname of your Splunk Heavy Forwarder (or IDM). For example, if the hostname of your HF or IDM is `example.splunk.link`, the Redirect URI you have to enter is:
    
    `https://example.splunk.link/en-US/splunkd/__raw/services/webex-teams-oauth`
    
    **Note**: If your Splunk site is not in `en-US`, please change it to your true value. 
    - **Scope**: Please select these three options 
       - Spark:all
       - Audit:events_read
       - Spark-compliance:events_read
- Click on `Add Integration` button.
- Please copy the `Client ID` and `Client Secret` somewhere for further use.


#### Configuration steps
The configuration steps are common for `on-prem` and `cloud`. Please follow the following steps in order:
- Open the Web UI for the Heavy Forwarder (or IDM).
- Access the TA from the list of applications.
- Click on `Configuration` button on the top left corner.
- Click on `Add-on Settings` button.
- Enter the following details:
  - **Redirect URI** (**_required_**): Please enter the Redirect URI of your Webex Teams Integration App. It **MUST** match the Redirect URI that is defined in your Webex Teams Integration configuration. For example, `https://{{hostname}}/en-US/splunkd/__raw/services/webex-teams-oauth`

  - **Client ID** (**_required_**): Please enter the Client ID of your Webex Teams Integration App that you create for this Add-on. 
  - **Client Secret** (**_required_**): Please enter the Client Secret of your Webex Teams Integration App that you create for this Add-on. 
- Click on the `Generate Tokens` green button.
After you click the `Generate Tokens` green button. You will be redirected to the Webex sign in page in the pop-up window. Please enter your email/username and password to login. Then click the `Accept` button to grant the permissions. You should see the Permissions Granted confirmation page with your Access Token and Refresh Token. Please **CLOSE** this page directly and go back to the Add-on configuration page.
- Click on the `Save` green button.

## Additional Configuration

### Logging

The Log-Level can be set in the "Logging" Tab.

Log Files can be found under:

* $SPLUNK_HOME/var/log/splunk/ta_dp_webex_teams_webex_teams_events.log for Events

* $SPLUNK_HOME/var/log/splunk/ta_dp_webex_teams_webex_teams_admin_audit_events.log for Audit Events

* $SPLUNK_HOME/var/log/splunk/webex_teams_oauth_handler.log for OAuth Flow

### General Configuration

In some cases, the Webex API did not give back a valid certificate. For all requests, it's possible to disable Certificate Verification.

### Proxy

For connections over a proxy, the settings can be found under "Configuration"

## Input Configuration

### Overview

Under Inputs, select which type of input should be created

### Creating Webex Teams Event Inputs

Following parameters have to be set for the input:

* Name
* Interval
* Index
* Resource
* Message Masking
* Fetch Attachemen Information
* Fetch Room Information

Events will be created with the webex:teams:events sourcetype.

## Creating Webex Teams Admin Audit Event Input

Following parameters have to be set for the input:

* Name
* Interval
* Index
* Organization ID

Events will be created with the webex:teams:adminaudit:events sourcetype.

## Release Notes
* 1.0.1 / 2020-08-04 Bugfix Release
* 1.0.0 / 2020-07-23 First Release
 
## Change Notes

* 2020-07-23 mbo
  * First Release
* 2020-08-04 mbo
  * Fixed in issue with too many token refreshes
* 2021-01-12
  * Added OAuth flow support
* 2021-01-14
  * Changed to use Events created date as checkpoint
  
## License

Copyright 2020 Datapunctum GmbH

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

## Sourcecode Repository

https://github.com/datapunctum/TA-DP-webex-teams
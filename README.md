 ### RapidPro External USSD Channel
 
RapidPro External USSD channel is an open source software that uses RapidPro's Generic External Channel 
API to relay messages between RapidPro and USSD supported devices through USSD aggregator APIs that 
are configurable within the channel.

### Setting up this channel
In order to use the USSD External Channel Service, you must have a fully installed and working instance of the supported RapidPro system (i.e. post v5). Please follow the setup instructions found [here](http://rapidpro.github.io/rapidpro/docs/):  

Once RapidPro is up and running, you can install and configure the channel service as detailed below.

The minimum requirements for the channel service are the same as those for RapidPro, specifically:

 * [Python v3.6](https://www.python.org/downloads/release/python-360/) and later

 * An RDBMS preferably [PostgreSQL 9.6](https://www.postgresql.org/) or later
 * [Redis 3.2](https://redis.io/) or later
 
This means that RapidPro and the channel service can co-exist on the same server instance.

The setup has been broken down into five simple steps described below.

### Database setup

Start the [Redis 3.2](https://redis.io/) server. 
 
You can use other RDMS like MySQL but we recommend  [PostgreSQL](https://www.postgresql.org/).



Create a new database user `ussd_user` for postgreSQL

You can create one by running this command in your terminal
```
$createuser ussd_user --pwprompt -d
```

Create database named `ussd` by running the command below
```
$createdb ussd
```

If all is well with your [PostgreSQL](https://www.postgresql.org/) then your database is ready.

### UI setup

Go on to clone the project [Here](https://github.com/dsmagicug/rapidpro-external-ussd-channel.git) by running the command below

```
$git clone https://github.com/dsmagicug/rapidpro-external-ussd-channel.git

$cd rapidpro-external-ussd-channel

```
#### Build a virtual environment
This step is optional but it's highly recommended to use a virtual environment to run your External USSD channel installation. The pinned python dependencies for the project can be found in pip-freeze.txt. You can build the recommended environment as follows (from the root External USSD channel installation directory):

```
$ virtualenv -p python3 env
$ source env/bin/activate
$(env) $ pip install -r pip-freeze.txt 
```
#### sync your database
Still inside your project root directory, run the following command 
```
$python manage.py migrate
```

#### collect static files
```
$python manage.py collectstatic
```
#### Start django server
```
$python manage.py runserver
```
## Running The channel and RapidPro on the same server instance
In most cases, you may want to install both [RapidPro](https://github.com/rapidpro/rapidpro) and the [External USSD channel](https://github.com/dsmagicug/rapidpro-external-ussd-channel.git) on the same server instance. 

To set up RapidPro follow the instructions [Here](http://rapidpro.github.io/rapidpro/docs/development/)

Since they are both Django applications, you have to run `python manage.py runserver` for each of them.
This will return an error (```Address already in use.```) since the Django development server by default runs on port `8000`.

The trick here is starting each application on a different port  as described in the django documentation [Here](https://docs.djangoproject.com/en/3.1/ref/django-admin/).

In this case, we shall use port `5000` to run the External USSD Channel development server

Inside the [External USSD channel](https://github.com/dsmagicug/rapidpro-external-ussd-channel.git) project directory run

```
python manage.py runserver 0.0.0.0:5000
```

Then you can visit http://localhost:5000 to access the web interface

We recommend that you leave RapidPro use the default port `8000`.


### Configuring External USSD channel to talk to RapidPro.

* Visit http://localhost:8000 or https://localhost:5000  as seen above.
**NOTE** You can use any free ports of your choice.
* Register a new an account.
* Login

With your [RapidPro](https://github.com/rapidpro/rapidpro) instance running either remotely or on the same machine,
 
 
 ### Channel Configurations
 
 Go to `CHANNEL CONFIGS` on the sidemenu to configure a channel and follow the Step by step instructions form.
 
 1. `SEND URL` This is a URL which RapidPro will call when sending an outgoing message.
 This URL will be generated as you input your local server URL required.
 
 The format of the SEND URL will be `http://yourmachine/adaptor/send-url`. 
 
 Copy this link,head to Rapidpro and paste it into RapidPro's
 External API form under the `Send url` field.
 
 2. Fill the rest of RapidPro's External API configuration form and then submit it.
 You will be presented with a page that has instructions on how to setup an external 
 service (The USSD External Channel) .
 
 3. On the above instructions pages in RapidPro, copy the `RECEIVE URL` and head back to the USSD channel form.
 
 4. Click Next and paste the `RECEIVE URL` there. (make sure the `https://app.rapidpro.io` part of this URL is 
 substituted with the correct link to your RapidPro instance and please leave the other part `/c/ex/......../receive` untouched).
 
 5. Click Next to configure the Channel's Max-timeout `(default=10s)`. This is the time in seconds our channel 
 waits for a response from RapidPro. 
 It times out if RapidPro does not reply within that time interval.
 
 6. Click Next to configure the Trigger word `(default=USSD)`. This is a keyword to trigger a given flow execution
 in Rapidpro when a contact starts a new session when it isn't involved with any RapidPro flows yet.
 
 7. Submit the form to save the channel configurations.
 
 
 
 #### Aggregator Handler Configurations
 
Since different USSD aggregator APIs have different Request/Response formats, 
this channel standardizes these formats into one understood by RapidPro.

This is achieved through configuring handlers for each of the aggregator APIs that you want to use.

To set up a Handler,

Go to `HANDLERS` on your side menu, click `Add Handler` button. 
You will then be presented with a form with the following fields;

 1. `Aggregator`: (the name of the USSD aggregator that you want to use 
 for example [DMARK](#) or [Africa's Talking](https://africastalking.com/ussd))
 
 2. `Shot code`: (The short code provided by your aggregator e.g `348`.)
 
 3. `Request format`: This is a very important field which must be set correctly 
 in order for the channel to safely standardize aggregator Requests.
 
 The template format is provided already in that text area as shown below.     
```
{{short_code=ussdServiceCode}},  {{session_id=transactionId}}, {{from=msisdn}}, {{text=ussdRequestString}}, {{date=creationTime}}
```

Each is a combination of two parameters, on either sides of the equal sign(`=`).

The one on the left represents the format understood by RapidPro and our External channel which *MUST* not change.

The one on the right hand side represents the format in which the aggregator requests delivers that value to our channel.

for example 
```
{{short_code=ussdServiceCode}},  {{session_id=transactionId}}, {{from=msisdn}},  {{text=ussdRequestString}}
``` 
means the request from the aggregator API in this case say `DMARK` will arrive as
```
{"ussdServiceCode:"257","transactionId":123456789, "msisdn":"25678xxxxxx","ussdRequestString":"Hello world"}
``` 
the above format will then be converted into 
```
{"short_code":"257", "session_id":123456789, "from":"25678xxxxxx", "text":"Hello World"}
``` 
which is understood by Rapidpro and our Channel.

for example if a particular aggregator represents `short_code` as `serviceCode`, the combination to map this will be `{{short_code=serviceCode}}`. 
Please refer to your respective aggregator USSD Docs for their formats.

Note that our channel and RapidPro have the following standard formats 
    -   **_session_id_** for USSD session ID
    -   **_short_code_** for USSD short codes e.g. `348`
    -   _**from**_ for the phone number in the Request.
    -   **_text_** for the content(message) in the request i.e. User replies.
    -    **_date_** (Optionally set) for the time string in the request.
    
Note that apart from `date`, your request format has to cater for all the rest by mapping them 
to their equivalents in the USSD request from a given aggregator API.


4. `Response content type`: this is how the response to the aggregator API should be encoded(default is `application/json`) 
(refer to your aggregator's USSD Docs for such information )

5. `Response method`: Specifies whether your aggregator expects a `POST`, `GET` or `PUT` method in the response. 

6. `Signal response string`: this is a keyword in the response to your aggregator's API that is used to signal further interaction in the USSD session,
i.e. a USSD menu with an inputbox for the end user to reply. (Refer to aggregator's USSD Docs for this keyword)

7. `Signal end string`: this is the Keyword your aggregator uses in the response string to indicate the end of a USSD Session in order to send a USSD prompt without an inputbox to the end user device.(Refer to aggregator's USSD Docs for this keyword)

8. `Response format`: This field indicates the format expected by the aggregator's API in the response from the channel.
Two options are provided, 

    - `Is Key Value:` (Default) means the aggregator API will accept the message and signal response string(seen above)  
       from our channel if its in a `json` like    key-value string e.g `{"responseString":"Hello User how are you": "signal":"request"}`
    - `Starts With`: means the aggregator expects a string in the response body that *starts* with a keyword to
       signal end or request for interaction as seen above.
    
9. `Response Structure`: if option 1 (Is Key Value)in 8 above is chosen, a text area will appear expecting entries discussed under `Request Format` in `(3)`   above.

With similar logic as in (3) above, our channel understands as follows
       -    `text` for the text(message) in the response
       -    `action` for the signal keywords set above.
       
for example if aggregator A's expected response is in this format; 
```
{"responseString":"Hello User how are you": "signal":"Signal_keyword"}
```
the entry in this field should then be 
```
{{text=responseString}}, {{action=signal}}
```
        
8. `Push support`: A boolean to specify whether your aggregator supports USSD PUSH protocal i.e MT USSD sessions (Default=`False`).


Submit this form and enjoy the power of RapidPro through USSD. 
You can configure multiple handlers for multiple aggregators but each aggregator must have one handler depending on the format of their requests/responses. 
 

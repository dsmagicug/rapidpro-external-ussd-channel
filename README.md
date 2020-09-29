 ##RapidPro External USSD channel
 This channel uses RapidPro's Generic External Channel API to relay messages between RapidPro and USSD supported devices through USSD aggregator APIs that are configurable within this channel.


### Setting up this channel
In order to run this channel for development, follow this quick guide.
Note that development and deployment has only been tested on OSX and Linux, you will likely have to modify a couple of steps below if using Windows.

### Prerequisites

 * [Python v3.6](https://www.python.org/downloads/release/python-360/) and later

 * An RDBMS preferably [PostgreSQL 9.6](https://www.postgresql.org/) or later
 * [Redis 3.2](https://redis.io/) or later



### Database setup
Start the [Redis 3.2](https://redis.io/) server. 
 
Let's use [PostgreSQL](https://www.postgresql.org/) as our database software.


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
## Running The channel and RapidPro on the same host machine
In most cases, you may want to install both [RapidPro](https://github.com/rapidpro/rapidpro) and our [External USSD channel](https://github.com/dsmagicug/rapidpro-external-ussd-channel.git) on the same local machine. 

To set up RapidPro follow the instructions [Here](http://rapidpro.github.io/rapidpro/docs/development/)

Since they are both Django applications, you may find your self needing to run `python manage.py runserver` for both cases and this will complain with a ```Address already in use.``` error since the Django development server by default runs on port `8000`.

The easiest trick here is starting each on a different port  as described in the django documentation [Here](https://docs.djangoproject.com/en/3.1/ref/django-admin/).
For our example, we shall use port `5000` to run the External USSD Channel development server

Inside the [External USSD channel](https://github.com/dsmagicug/rapidpro-external-ussd-channel.git) project directory run

```
python manage.py 0.0.0.0:5000
```

Then you can visit http://localhost:5000 to access the web interface

We recommend that you leave RapidPro use the default port `8000`


## Configuring External USSD channel to communicate to RapidPro.

* Visit http://localhost:8000 or https://localhost:5000  as seen above.
**NOTE** You can use any free ports of your choice.
* Register a new an account.
* Login

With your [RapidPro](https://github.com/rapidpro/rapidpro) instance running either remotely or on the same machine,
 
 ####CHANNEL CONFIGURATIONS
 
 Go to `CHANNEL CONFIGS` on the sidemenu to configure a channel closely following the instructions on the Step by step form.
 Note  that you will need to configure the following for your channel to work properly. 
 1. `SEND URL` This is a URL which RapidPro will call when sending an outgoing message.
 This URL will be generate for you as you key in your machine URL which the form requires you to provide.
 The SEND URL will be in a format like this; `http://yourmachine/adaptor/send-url`. Copy this link, quickly head to Rapidpro and paste it into RapidPro's
 External API form under the `Send url` field.
 
 2. Fill the rest of RapidPro's External API configuration form and then submit it.
 You will be presented with a page that has instructions on how to setup an external service,fortunately our USSD channel is the said service in this case.
 
 3. On the above instructions pages in RapidPro, we are ONLY interested in the `RECEIVE URL` copy it and head back to our USSD channel form.
 4. Click Next and paste the URL there. (make sure the `https://app.rapidpro.io` part of this URL is substituted with the correct link to your RapidPro instance and please leave the other part `/c/ex/......../receive` untouched).
 5. Click Next to configure the Channel's Max-timeout `(default=10s)`. This is the time in seconds our channel shall wait for a response from RapidPro. It will time out if RapidPro does not reply within that time interval.
 6. Click Next to configure the Trigger word `(default=USSD)`. This is a keyword to trigger a given flow execution in Rapidpro when a contact starts a new session when it isn't involved with any RapidPro flows yet.
 7. Submit the form to save the channel configurations.
 
 #### AGGREGATOR HANDLER CONFIGURATIONS
 
 Since different USSD aggregator APIs have different Request/Response formats, this channel provides a way to standardize these formats into one commonly understood by RapidPro.
 This is achieved through configuring handlers for each one of the aggregator APIs that you want to use.
 
 To set up a Handler,
 
 Go to `HANDLERS` on your side menu, click `Add Handler` button, You will be presented with a form with the following fields
 1. `Aggregator`: (the name of the USSD aggregator that you want to use for example [DMARK](#) or [Africa's Talking](https://africastalking.com/ussd))
 2. `Shot code`: (Short code you are provided with by your aggregator e.g `348`.)
 3. `Request format`: This is a very important field which you MUST have right so as the channel can safely standardize aggregator Requests to RapidPro understandable ones.
  The template format is provided already in that textarea as shown below. 
    
    ```
    {{short_code=ussdServiceCode}},  {{session_id=transactionId}}, {{from=msisdn}}, {{text=ussdRequestString}}, {{date=creationTime}}
    ```

    Each is a combination of two parameters, one on the left hand side of the equal sign(`=`) and the other on the left.
The one on the let represents the format understood by RapidPro and our External channel which *MUST* not change.
The one on the right hand side represents the format in which the aggregator requests delivers that value to our channel.

    for example 
    ```
    {{short_code=ussdServiceCode}},  {{session_id=transactionId}}, {{from=msisdn}},  {{text=ussdRequestString}}
    ``` 
    means the request from the aggregator API in this case say `DMARK` will arrive as
     ```
     {"ussdServiceCode:"257","transactionId":123456789, "msisdn":"25678xxxxxx","ussdRequestString":"Hello world"}
    ``` 
    This format will then be converted into 
    ```
    {"short_code":"257", "session_id":123456789, "from":"25678xxxxxx", "text":"Hello World"}
    ``` 
    which is understood by Rapidpro and our Channel.
for example if a particular aggregator represents `short_code` as `serviceCode`, the combination to map this will be `{{short_code=serviceCode}}`. Please refer to your respective aggregator USSD Docs for their formats.

    Note that our channel and RapidPro have the following standard formats 
    -   **_session_id_** for USSD session ID
    -   **_short_code_** for USSD short codes e.g. `348`
    -   _**from**_ for the phone number in the Request.
    -   **_text_** for the content(message) in the request i.e. User replies.
    -    **_date_** (Optionally set) for the time string in the request.
    Note that apart from `date`, your request format has to cater for all the rest by mapping them to their equivalents in the USSD request from a given aggregator API.
4. `Response content type`: how the response to the aggregator API should be encoded(default is `application/json`) (refer to your aggregator's USSD Docs for such information )
5. `Response method` (whether your aggregator expects a `POST`, `GET` or `PUT` method in the response) 
6.  `Signal response string`: this is a keyword in the response to your aggregator's API that is used to signal further interaction in the USSD session, i.e. a USSD menu with an inputbox for the end user to reply. (Refer to aggregator's USSD Docs for this keyword)
7.  `Signal end string`: this is the Keyword your aggregator uses in the response string to indicate end of USSD Session in order to send a USSD prompt without an inputbox to the end user device.(Refer to aggregator's USSD Docs for this keyword)
8.  `Response format`: This field indicates the format expected by the aggregator's API in the response sent by our channel.
two options are so far provided, 
    - `Is Key Value:` (Default) means the aggregator API will accept the message and signal response string(seen above)  from our channel if its in a `json` like key-value string e.g `{"responseString":"Hello User how are you": "signal":"request"}`
    - `Starts With`: means the aggregator expects a string in the response body that *starts* with a keyword to signal end or request for interaction as seen above.
9.  `Response format` template: if option 1 (Is Key Value)in 8 above is chosen, a textarea will come from hiding expecting entries discussed under `Request Format` in `(3)` above.
    with similar logic, our channel understands as follows
       -    `text` for the text(message) in the response
       -    `action` for the signal keywords set above.
       for example if aggregator A's response should be in this format 
       ```
       {"responseString":"Hello User how are you": "signal":"Signal_keyword"}
       ```
       the entry in this field will be 
       ```
       {{text=responseString}}, {{action=signal}}
        
8.  `Push support`: Boolean to specify whether your aggregator supports USSD PUSH protocal i.e MT USSD sessions (Default=`False`)


Submit this form and you are ready to enjoy the power of RapidPro through USSD. You can configure multiple handlers for multiple aggregators but each aggregator must have one handler depending on the format of their requests. 
 
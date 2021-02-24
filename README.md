 ### RapidPro External USSD Channel
 
RapidPro External USSD channel is an open source software that uses RapidPro's Generic External Channel 
API to relay messages between RapidPro and USSD supported devices through USSD aggregator APIs that 
are configurable within the channel.

### Setting up this channel
In order to use the USSD External Channel Service, you must have a fully installed and working instance of the supported RapidPro system (i.e. post v5). Please follow the setup instructions found [here](http://rapidpro.github.io/rapidpro/docs/):  

Once RapidPro is up and running, you can install and configure the channel service as detailed below.

The minimum requirements for the channel service are the same as those for RapidPro, specifically:

 * [Python >= v3.6](https://www.python.org/downloads/release/python-360/) and later

 * An RDBMS preferably [PostgreSQL 10](https://www.postgresql.org/) or later
 * [Redis >= v5.0](https://redis.io/) or later
 
This means that RapidPro and the channel service can co-exist on the same server instance.

The setup has been broken down into five simple steps described below.

### Database setup

Start the [Redis](https://redis.io/) server. 
 
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
Django countries  requires you populate the Countries table with the latest country data using
```
$python manage.py update_countries_plus
```
#### collect static files
```
$python manage.py collectstatic
```
#### Start django server
```
$python manage.py runserver
```
### Running The channel and RapidPro on the same server instance
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
 service (The USSD External Channel).
 
    **NOTE**: Before submiting RapidPro's External API configuration form, make sure you add cgi params 
    
    ```session_status={{session_status}}&to_no_plus={{to_no_plus}}&from_no_plus={{from_no_plus}}```
    
    to the `Request Body` field. These are required when rapidPro is making a request to the USSD external channel in addition to the default 
    
    ```id={{id}}&text={{text}}&to={{to}}&from={{from}}&channel={{channel}}```.
    
    Your configuration will not work if these cgi-params are not set at this level since the channel uses `session_status` within the request from RapidPro to tell if the interaction is still ongoing or completed so as it initiates the right USSD menu to the end user device. If you are confused, just copy
    
    ```id={{id}}&text={{text}}&to={{to}}&to_no_plus={{to_no_plus}}&from={{from}}&from_no_plus={{from_no_plus}}&channel={{channel}}&session_status={{session_status}}``` 
    
    and paste it in Request Body field.
 
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
 
 2. `Shortcode`: (The USSD shortcode returned by the aggregator in the response string e.g `255*4`.If aggregator does not return one in the response, please set one in settings.DEFAULT_SHORT_CODE and use that here.)
 
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

   - **_session_id_** for USSD session ID
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

   -  `text` for the text(message) in the response
   -   `action` for the signal keywords i.e (the ones that signale end of session or more interaction as discussed above).
       
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
 
### RapidPro USSD Flow Setup and best Practices

Although the channel does not require much changes in the normal RapidPro SMS flows, for a swift experience using this channel, you may want to revisit your SMS flow designs to best serve USSD. Below we present you our recommended best practices.


 * Create a RapidPro trigger that corresponds to the `Trigger word` that was specified during `step 6` under Channel config above.
 * If you want a single shortcode to support multiple flows, create a single flow that routes to other flows and assign a the trigger (create in above) to that flow. for example if You have 3 flows (Register flow, Login flow, and Survey flow), you can create an extra flow say  `Link flow` and route the user accordingly as below.
```
 1. Register
 2. Login
 3. Survey
 ```

 * Ensure that there are no open nodes in the flows, for example if a node (a step in flow) requires a user to provide options as below; 
 ```
 1. Yes
 2. No
 3. Opt out
 4. Back to main menu
 ```
 Your flow should have a node that handles a scenario where a user enters a 5 or anything undesirable. This is normally provided by RapidPro using the route called `Other`. Make sure `Other` is handled and not left open. i.e. you can create a node that notifies the user of a wrong entry and routes back to waiting another entry. Failure to handle `Other` may result into bad channel behaviour which can be frustrating.

 * When designing your flows for USSD, make sure the user does not have to enter long responses whenever you can. e.g. provide options to pick from as numbers (1,2,3,4,5....) like in the above examples.

 * Its good practice to provide an option for Cancelling and routing back to the previous step or back to main menu  in your flows. For example
 ```
 1. Yes
 2. No
 3. Back
 4. Back to main menu
 5. Cancel(Opt out)
 ```
 * Lastly, RapidPro provides a flow feature which expires inactive contacts after a give period of time, make sure you specify this period during or after flow creation to avoid scenarios where a contact who dailed a shortcode a month ago and probably forgot where they stopped,comes back and picks up from where they left off. You may want to set the flows to restart these cases afresh.

### Deployment (enable Live session tracking table)
We have looked at setting up a development server for this channel above. let us look at how quickly you can set up an instance for production.  

The External Channel applications uses [Django Channels](https://channels.readthedocs.io/en/stable/index.html)

Channels is a project that takes Django and extends its abilities beyond HTTP - to handle WebSockets, chat protocols, IoT protocols, and more. It’s built on a Python specification called [ASGI](http://asgi.readthedocs.io/)

In order to support live session table on the dashboard i.e. whenever a user initiates a USSD session, it can be visible in realtime on the graph and table on the dashboard. This ability uses websockets which if not deployed well may disable the feature. 

Note that this has no negative effects on the overall performance of the system. It just grants you the ability to watch USSD sessions as they are initiated in realtime. If you are excited about this feature, we offer you an easy way of getting started.

 * The system comes with [Daphne](https://pypi.org/project/daphne/) which is a HTTP, HTTP2 and WebSocket protocol server for ASGI and ASGI-HTTP, developed to power Django Channels.

 * The system has an `asgi.py` file under `project_folder/core/` which is ready to get you started quickly. What you need to do is simply run `daphne -b 0.0.0.0 -p 8000 core.asgi:application`
 inside your project directory and you are good to go. You can run daphne user a python virtual environment by simply using `venv/bin/daphne -b 0.0.0.0 -p 8000 core.asgi:application`

 You can run this as a daemon if you want using [systemd](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwia1-WAkcHtAhVbilwKHSD2AFgQFjAKegQIIhAC&url=https%3A%2F%2Fwiki.archlinux.org%2Findex.php%2Fsystemd&usg=AOvVaw0gaiXnpOAFuudxBlQMopBx) or similar projects on Linux or macOS.

There are also alternative ASGI servers that you can use for serving Channels as described [here](https://channels.readthedocs.io/en/stable/deploying.html)

Another important resource on this can be found [here](https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/daphne/)

You can as well deploy the system using `wsgi` and it will still work, except you won't get a live session tracking table on your dashboard. Under this setup, you can only see new USSD sessions after reloading the page.
But the graphs will still give you a relatively better update of what's happening.

Thank you.

Good luck.
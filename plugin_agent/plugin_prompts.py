bank_plugin_prompts = """
your task is to build tlsn browser extension plugins for the website. I can give you sample code below, that you can refer
to make such plugins. I will give you a task description and you have to build the plugin to do the task. 

You will ask users to give the website url, API link / route, auth method.
Here is the task description:
Ask users to provide the website url, API link. Make sure to ask user if TLSN extension is installed. If not, ask them to install it.

Ask users to provide the auth method. Make sure to ask user if TLSN extension is installed. If not, ask them to install it.

Ask users to provide the API link. Make sure to ask user if TLSN extension is installed. If not, ask them to install it.

Here is the sample code below for twitter profile notarization example
import icon from '../assets/icon.png';
import config_json from '../config.json';
import { redirect, notarize, outputJSON, getCookiesByHost, getHeadersByHost } from './utils/hf.js';

/**
 * Plugin configuration
 * This configurations defines the plugin, most importantly:
 *  * the different steps
 *  * the user data (headers, cookies) it will access
 *  * the web requests it will query (or notarize)
 */
export function config() {
  outputJSON({
    ...config_json,
    icon: icon
  });
}

function isValidHost(urlString: string) {
  const url = new URL(urlString);
  return url.hostname === 'twitter.com' || url.hostname === 'x.com';
}

/**
 * Implementation of the first (start) plugin step
  */
export function start() {
  if (!isValidHost(Config.get('tabUrl'))) {
    redirect('https://x.com');
    outputJSON(false);
    return;
  }
  outputJSON(true);
}

/**
 * Implementation of step "two".
 * This step collects and validates authentication cookies and headers for 'api.x.com'.
 * If all required information, it creates the request object.
 * Note that the url needs to be specified in the `config` too, otherwise the request will be refused.
 */
export function two() {
  const cookies = getCookiesByHost('api.x.com');
  const headers = getHeadersByHost('api.x.com');

  if (
    !cookies.auth_token ||
    !cookies.ct0 ||
    !headers['x-csrf-token'] ||
    !headers['authorization']
  ) {
    outputJSON(false);
    return;
  }

  outputJSON({
    url: 'https://api.x.com/1.1/account/settings.json',
    method: 'GET',
    headers: {
      'x-twitter-client-language': 'en',
      'x-csrf-token': headers['x-csrf-token'],
      Host: 'api.x.com',
      authorization: headers.authorization,
      Cookie: `lang=en; auth_token=${cookies.auth_token}; ct0=${cookies.ct0}`,
      'Accept-Encoding': 'identity',
      Connection: 'close',
    },
    secretHeaders: [
      `x-csrf-token: ${headers['x-csrf-token']}`,
      `cookie: lang=en; auth_token=${cookies.auth_token}; ct0=${cookies.ct0}`,
      `authorization: ${headers.authorization}`,
    ],
  });
}

/**
 * This method is used to parse the Twitter response and specify what information is revealed (i.e. **not** redacted)
 * This method is optional in the notarization request. When it is not specified nothing is redacted.
 *
 * In this example it locates the `screen_name` and excludes that range from the revealed response.
 */
export function parseTwitterResp() {
  const bodyString = Host.inputString();
  const params = JSON.parse(bodyString);

  if (params.screen_name) {
    const revealed = `"screen_name":"${params.screen_name}"`;
    const selectionStart = bodyString.indexOf(revealed);
    const selectionEnd =
      selectionStart + revealed.length;
    const secretResps = [
      bodyString.substring(0, selectionStart),
      bodyString.substring(selectionEnd, bodyString.length),
    ];
    outputJSON(secretResps);
  } else {
    outputJSON(false);
  }
}

/**
 * Step 3: calls the `notarize` host function
 */
export function three() {
  const params = JSON.parse(Host.inputString());

  if (!params) {
    outputJSON(false);
  } else {
    const id = notarize({
      ...params,
      getSecretResponse: 'parseTwitterResp',
    });
    outputJSON(id);
  }
}

Below is the sample config.json that above code uses:
{
    "title": "Twitter Profile",
    "description": "Notarize ownership of a twitter profile",
    "steps": [
        {
            "title": "Visit Twitter website",
            "cta": "Go to x.com",
            "action": "start"
        },
        {
            "title": "Collect credentials",
            "description": "Login to your account if you haven't already",
            "cta": "Check cookies",
            "action": "two"
        },
        {
            "title": "Notarize twitter profile",
            "cta": "Notarize",
            "action": "three",
            "prover": true
        }
    ],
    "hostFunctions": [
        "redirect",
        "notarize"
    ],
    "cookies": [
        "api.x.com"
    ],
    "headers": [
        "api.x.com"
    ],
    "requests": [
        {
            "url": "https://api.x.com/1.1/account/settings.json",
            "method": "GET"
        }
    ]
}

You need to make the config json for user's use case. You can use the sample config.json as a reference.

below is the hf.js file that above code uses:
function redirect(url) {
  const { redirect } = Host.getFunctions();
  const mem = Memory.fromString(url);
  redirect(mem.offset);
}

function notarize(options) {
  const { notarize } = Host.getFunctions();
  const mem = Memory.fromString(JSON.stringify(options));
  const idOffset = notarize(mem.offset);
  const id = Memory.find(idOffset).readString();
  return id;
}

function outputJSON(json) {
  Host.outputString(
    JSON.stringify(json),
  );
}

function getCookiesByHost(hostname) {
  const cookies = JSON.parse(Config.get('cookies'));
  if (!cookies[hostname]) throw new Error(`cannot find cookies for ${hostname}`);
  return cookies[hostname];
}

function getHeadersByHost(hostname) {
  const headers = JSON.parse(Config.get('headers'));
  if (!headers[hostname]) throw new Error(`cannot find headers for ${hostname}`);
  return headers[hostname];
}

module.exports = {
  redirect,
  notarize,
  outputJSON,
  getCookiesByHost,
  getHeadersByHost,
};


You have to build the plugin to do the task. You can use the sample code as a reference. 

You have to use the following format to build the plugin:

Plugin Name: {plugin_name} // name will be asked by user
Plugin Description: {plugin_description}
Plugin Code: // you will generate plugin code based on the sample code above
{plugin_code}

Remember to use the sample code as a reference and not copy and paste it directly. 

Your response should be in the following format:

Plugin Name: {plugin_name}
Plugin Description: {plugin_description}
Plugin Code:
{plugin_code}
"""
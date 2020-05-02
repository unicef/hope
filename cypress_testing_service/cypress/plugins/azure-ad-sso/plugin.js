// https://gist.github.com/csuzw/845b589549b61d3a5fe18e49592e166f
'use strict';

const puppeteer = require('puppeteer');

/**
 *
 * @param {options.username} string username
 * @param {options.password} string password
 * @param {options.loginUrl} string password
 * @param {options.postLoginSelector} string a selector on the app's post-login return page to assert that login is successful
 * @param {options.headless} boolean launch puppeteer in headless more or not
 * @param {options.logs} boolean whether to log cookies and other metadata to console
 * @param {options.getAllBrowserCookies} boolean whether to get all browser cookies instead of just for the loginUrl
 */
module.exports.AzureAdSingleSignOn = async function AzureAdSingleSignOn(
  options = {},
) {
  validateOptions(options);

  const browser = await puppeteer.launch({ headless: !!options.headless });
  const page = await browser.newPage();
  await page.goto(options.loginUrl);

  await typeUsername({ page, options });
  await typePassword({ page, options });

  const cookies = await getCookies({ page, options });

  await finalizeSession({ page, browser, options });

  return {
    cookies,
  };
};

function validateOptions(options) {
  if (!options.username || !options.password) {
    throw new Error('Username or Password missing for login');
  }
  if (!options.loginUrl) {
    throw new Error('Login Url missing');
  }
  if (!options.postLoginSelector) {
    throw new Error('Post login selector missing');
  }
}

async function typeUsername({ page, options } = {}) {
  await page.waitForSelector('input[name=loginfmt]:not(.moveOffScreen)', {
    visible: true,
    delay: 10000,
  });
  await page.type('input[name=loginfmt]', options.username, { delay: 50 });
  await page.click('input[type=submit]');
}

async function typePassword({ page, options } = {}) {
  await page.waitForSelector(
    'input[name=Password]:not(.moveOffScreen),input[name=passwd]:not(.moveOffScreen)',
    { visible: true, delay: 10000 },
  );
  await page.type('input[name=passwd]', options.password, { delay: 50 });
  await page.click('input[type=submit]');
  await page.waitForSelector('input[name=DontShowAgain]:not(.moveOffScreen)', {
    visible: true,
    delay: 10000,
  });
  await page.click('input[type=submit]');
}

async function getCookies({ page, options } = {}) {
  await page.waitForSelector(options.postLoginSelector, {
    visible: true,
    delay: 10000,
  });
  const cookies = options.getAllBrowserCookies
    ? await getCookiesForAllDomains(page)
    : await page.cookies(options.loginUrl);

  if (options.logs) {
    console.log(cookies);
  }

  return cookies;
}

async function getCookiesForAllDomains(page) {
  const cookies = await page._client.send('Network.getAllCookies', {});
  return cookies.cookies;
}

async function finalizeSession({ page, browser, options } = {}) {
  await browser.close();
}

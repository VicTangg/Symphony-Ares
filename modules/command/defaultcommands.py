import requests

import modules.botlog as botlog
import modules.botconfig as botconfig
import modules.crypto as crypto
import modules.symphony.messaging as messaging


def SendSymphonyEcho(messageDetail):
    msg = messageDetail.Command.MessageText
    messaging.SendSymphonyMessage(messageDetail.StreamId, msg)


def GetGoogleTranslation(messageDetail):
    transText = messageDetail.Command.MessageText

    if transText:
        payload = {"client": "gtx", "sl": "auto", "tl": "en", "dt": "t", "q": transText}
        transEP = "https://translate.googleapis.com/translate_a/single"

        response = requests.get(transEP, params=payload).json()
        translation = response[0][0][0]
        lang = response[2]

        msg = 'I think you said: ' + translation + ' (' + lang + ')'
    else:
        msg = 'Please include a word or sentence to be translated.'

    messaging.SendSymphonyMessage(messageDetail.StreamId, msg)


# https://www.alphavantage.co/documentation/
def GetAlphaVantageStockQuote(messageDetail):

    quoteText = messageDetail.Command.MessageText

    try:
        avAPIKey = botconfig.GetCommandSetting('alphavantage')['apikey']

        quoteSymbol = quoteText.split()[0]

        payload = {"function": "TIME_SERIES_DAILY", "apikey": avAPIKey, "symbol": quoteSymbol}
        avEP = 'https://www.alphavantage.co/query'
        response = requests.get(avEP, params=payload).json()

        tsDate = sorted(list(response['Time Series (Daily)'].keys()), reverse=True)[0]
        tsOpen = response['Time Series (Daily)'][tsDate]['1. open']
        tsClose = response['Time Series (Daily)'][tsDate]['4. close']

        msg = 'Quote for: ' + quoteText + '<br/>Date: ' + tsDate + '<br/>Open: ' + tsOpen
        msg += '<br/>Close: ' + tsClose + ''

        messaging.SendSymphonyMessage(messageDetail.StreamId, msg)

    except Exception as ex:
        errorStr = "Symphony REST Exception (system): {}".format(ex)
        botlog.LogSystemError(errorStr)
        msg = "Sorry, I could not return a quote."
        messaging.SendSymphonyMessage(messageDetail.StreamId, msg)


def GetGiphyImage(messageDetail):
    try:
        giphyAPIKey = botconfig.GetCommandSetting('giphy')['apikey']

        giphyText = messageDetail.Command.MessageText

        paramList = giphyText.split()

        isRandom = len(paramList) == 0 or paramList[0] == 'random'

        if isRandom:
            ep = "http://api.giphy.com/v1/gifs/random"
            payload = {"apikey": giphyAPIKey}
        else:
            ep = "http://api.giphy.com/v1/gifs/translate"
            payload = {"apikey": giphyAPIKey, "s": giphyText}

        response = requests.get(ep, params=payload).json()

        if isRandom:
            msg = "<a href='" + response['data']['image_original_url'] + "'/>"
        else:
            msg = "<a href='" + response['data']['images']['original']['url'] + "'/>"

        messaging.SendSymphonyMessage(messageDetail.StreamId, msg)

    except Exception as ex:
        errorStr = "Symphony REST Exception (system): {}".format(ex)
        botlog.LogSystemError(errorStr)
        msg = "Sorry, I could not return a GIF right now."
        messaging.SendSymphonyMessage(messageDetail.StreamId, msg)


def SendUserFeedbackHelp(messageDetail):
    msg = "Client Feedback Submission Help <br/><br/>"
    msg += "Syntax: <br/>"
    msg += "<ul><li>1. Activate the bot with either <hash tag='usability'/> or <hash tag='newfeature'/></li>"
    msg += "<li>2. Write a succinct title of the issue (50 characters).</li>"
    msg += "<li>3. Add additional detail of the issue - context of the user's usage and what problem " \
           "needs to be solved.</li>"
    msg += "<li>4. @mention users - they will be included as Watchers in JIRA.</li>"
    msg += "<li>5. Add screenshots which will also be forwarded to JIRA</li>"
    msg += "<li>6. End with <hash tag='clients'/> and then a comma separated list of client names.</li> </ul><br/><br/>"
    msg += "<hash tag='usability'/> = 'It is very difficult for the user to use an existing functionality.'<br/>"
    msg += "<hash tag='newfeature'/> = 'This would make the user's life easier if this feature was added.'<br/>"
    msg += "<br/>For <b>more information</b>, go to Confluence: <a href='http://bit.ly/2sezQN9'/>"

    messaging.SendSymphonyMessage(messageDetail.StreamId, msg)


def SubmitUserFeedback(messageDetail):
    import modules.plugins.Salesforce.commands as sfdc

    sfdc.SubmitUserFeedback(messageDetail)
    

def RemoteShutdown(messageDetail):
    if messageDetail.Command.UnnamedParams and len(messageDetail.Command.UnnamedParams):
        pwd = messageDetail.Command.UnnamedParams[0]

        pwdHash = '14811b20d51133c29fd0f19e3f7d7ef3b48ccae559e3c22b65542ba144c1750f'

        if crypto.CompareHashDigest(pwd, pwdHash):
            messageDetail.ReplyToSender("Shutting down Ares now.")
            botlog.LogSystemInfo("Shutdown command received from " + messageDetail.Sender.Email)
            exit(0)
        else:
            messageDetail.ReplyToSender("Incorrect password, baka.")
    else:
        messageDetail.ReplyToSender("You must specify a password.")


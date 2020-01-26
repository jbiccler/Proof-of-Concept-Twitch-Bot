import socket
import os


class Channel:
    def __init__(self, chan):
        self.chan = chan
        self.commands = {
            "hello": "self.hi()",
            "hi": "self.hi()",
            "hey": "self.hi()",
            "mrdestructoid": "self.sendMsg('MrDestructoid Beep Boop')",
            "!add": "self.addCommand(self.msgRecv)",
        }

    def join(self):
        ircsock.send(bytes("JOIN #" + self.chan + "\n", "UTF-8"))
        ircmsg = ""
        while ircmsg.find("End of /NAMES list") == -1:
            ircmsg = ircsock.recv(2048).decode("UTF-8")
            print(ircmsg)
        print("Successfully joined the channel: " + self.chan)
        ircsock.send(
            bytes("PRIVMSG #" + self.chan + " :" + "joined the channel" + "\n", "UTF-8")
        )


class Message:
    pongIter = 0

    def __init__(self, typeOfMsg, author="", channel="", msgRecv=""):
        self.type = typeOfMsg
        self.author = author
        self.channel = channel
        self.msgRecv = msgRecv

    def pong(self):
        Message.pongIter += 1
        print("Pong nr: " + str(Message.pongIter))
        ircsock.send(bytes("PONG :tmi.twitch.tv", "UTF-8"))

    def sendMsg(self, msg):
        ircsock.send(
            bytes("PRIVMSG #" + self.channel + " :" + r"{}".format(msg) + "\n", "UTF-8")
        )

    def hi(self):
        self.sendMsg("Hi, @" + self.author.title())

    def addCommand(self, msg):
        try:
            msg = msg[5:]
            name = msg.split(" ", 1)[0]
            descr = msg.split(" ", 1)[1].replace("'", r"\'").replace('"', r"\"")
            channels[self.channel].commands[name] = f"self.sendMsg('{descr}')"
        except:
            self.sendMsg("Invalid syntax, use !add !newCommand <answer>")

    def privmsg(self):
        try:
            commands = channels[self.channel].commands
            for i in commands.keys():
                if i in self.msgRecv.lower().replace(",", " ").split(" "):
                    print(commands[i])
                    eval(commands[i])
                    break
        except:
            pass


def process(rawMsg):
    if rawMsg.startswith("PING"):
        PingMsg = Message("PING")
        PingMsg.pong()

    elif "PRIVMSG" in rawMsg:
        author = rawMsg.split("!", 1)[0][1:].strip()
        typeOfMsg = rawMsg.split("tmi.twitch.tv ", 1)[1].split(" ", 1)[0].strip()
        channel = rawMsg.split("#", 1)[1].split(" ", 1)[0].strip()
        msg = rawMsg.split("#" + channel + " :", 1)[1].strip()
        RecvMsg = Message(typeOfMsg, author, channel, msg)
        RecvMsg.privmsg()


if __name__ == "__main__":
    # connect to the Twitch IRC server.
    server = "irc.chat.twitch.tv"
    port = 6667
    oauth = os.environ["TMI_TOKEN"]
    botnick = os.environ["BOT_NICK"]
    ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ircsock.connect((server, port))
    ircsock.send(bytes("PASS" + " " + oauth + "\n", "UTF-8"))
    ircsock.send(bytes("NICK" + " " + botnick + "\n", "UTF-8"))

    channels = {}
    for i in os.environ["CHANNEL"].split(","):
        channels[i] = Channel(i)
        channels[i].join()

    while 1:
        rawMsg = ircsock.recv(2048).decode("UTF-8")
        print(rawMsg)
        process(rawMsg)

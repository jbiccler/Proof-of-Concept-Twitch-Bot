import socket
import os

# Connecting

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "irc.chat.twitch.tv"
channel = os.environ["CHANNEL"].lower()
botnick = os.environ["BOT_NICK"]
port = 6667

ircsock.connect((server, port))
ircsock.send(bytes("PASS" + " " + os.environ["TMI_TOKEN"] + "\n", "UTF-8"))
ircsock.send(bytes("NICK" + " " + botnick + "\n", "UTF-8"))


def joinchan(chan):
    ircsock.send(bytes("JOIN #" + chan + "\n", "UTF-8"))
    ircmsg = ""
    while ircmsg.find("End of /NAMES list") == -1:
        ircmsg = ircsock.recv(2048).decode("UTF-8")
        # ircmsg = ircmsg.strip("nr")
        print(ircmsg)
    print("Successfully joined the channel")


def ping():
    ircsock.send(bytes("PONG :tmi.twitch.tv", "UTF-8"))


def sendmsg(msg, target=channel):
    ircsock.send(bytes("PRIVMSG #" + target + " :" + msg + "\n", "UTF-8"))
    print("Sent: " + "PRIVMSG #" + target + " :" + msg + "\n")


def commands(com, msg=""):
    coms = {
        "add": str(sum(map(int, msg.split(" + ")))),
        "lorem": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    }
    res = coms.get(com, "Not a valid command")
    sendmsg(res)
    return res


def main():
    joinchan(channel)
    sendmsg("test")
    while 1:
        print("loop iterated")
        ircmsg = ircsock.recv(2048).decode("UTF-8")
        # ircmsg = ircmsg.strip('nr')
        print(ircmsg)
        if ircmsg.find("PRIVMSG") != 1:
            name = ircmsg.split("!", 1)[0][1:]
            message = ircmsg.split("PRIVMSG", 1)[1].split(":", 1)[1]
            print(name + " :" + message)
            if message[0] == "!":
                print(commands(*message[1:].split(" ", 1)))
        elif ircmsg.find("PING :") != -1:
            ping()
            print("sent pong")


if __name__ == "__main__":
    main()

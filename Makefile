SWITCHES=3
HOSTS=4
DURATION=30
QUEUE=fifo
.PHONY: install run clear clean

install:
	sudo apt install python git mininet -y vlc*
	git clone git://github.com/mininet/mininet
	mininet/util/install.sh -a

run:
	sudo python src/topology.py --switches=$(SWITCHES) --hosts=$(HOSTS) --duration=$(DURATION) --queue=$(QUEUE)

clear:
	rm -rf mininet oflops oftest openflow pox

clean:
	sudo mn -c
	

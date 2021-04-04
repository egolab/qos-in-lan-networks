.PHONY: install run clear clean

install:
	sudo apt install python git mininet -y vlc*
	git clone git://github.com/mininet/mininet
	mininet/util/install.sh -a

run:
	sudo python src/topology.py

clear:
	rm -rf mininet oflops oftest openflow pox

clean:
	sudo mn -c
	

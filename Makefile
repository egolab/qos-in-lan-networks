.PHONY: install run clean

install:
	sudo apt install python git mininet -y vlc*
	git clone git://github.com/mininet/mininet
	mininet/util/install.sh -a

run:
	sudo python src/topology.py

clean:
	rm -rf mininet oflops oftest openflow pox
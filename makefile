SHELL:=powershell

PROJECT_NAME:=OnlineTimer

all: 
	mcdreforged pack
	mv -Force ${PROJECT_NAME}-v*.mcdr build

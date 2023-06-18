
act:
	source venv/bin/activate

upload:
	python upload_video.py --file="./meeting.mov" \
                       --title="UTML Meeting 2023/06/16" \
                       --description="Stable Diffusion Lab #02" \
                       --keywords="AI,api,programming" \
                       --category="22" \
                       --privacyStatus="public" \
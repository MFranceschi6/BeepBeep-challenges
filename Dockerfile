FROM python
MAINTAINER "Butter Group"
EXPOSE 5003
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . .
RUN python setup.py develop
CMD ["beepbeep-challenges"]
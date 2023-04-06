install:
	pip install -r requirements.in
	python -m ipykernel install --sys-prefix

clean: clean-run clean-s3

clean-run:
	rm -rfv $(PWD)/run/data/*

clean-s3:
	s3cmd --verbose del --force --recursive s3://keynslug-emqx-s3-demo/

## Tests
Test your code and make sure it passes.
cram is used for tests.
To install the test suite and run the tests, we recommend using Docker via the provided [Dockerfile](test/Dockerfile).
```shell
# Build image
docker build  -f test/Dockerfile --tag ogr2osm-test
```
```shell
# Run tests
docker run -it --rm -v ./:/app ogr2osm-test test/basic_usage.t \
  test/osm_output.t \
  test/pbf_output.t
```
See the GitHub actions file [test.yml](.github/workflows/test.yml) for more details.

Changes in speed-critical parts of the code may require profiling.

## Licensing

ogr2osm is under the MIT license. If you are committing to ogr2osm, 
you are committing under this license. If you do not wish to do so, 
do not submit pull requests.

If you wish to be added to the copyright holders list, submit a pull 
request.


![Python CI](https://github.com/getditto/interface-gen/workflows/Python%20CI/badge.svg)

# Interface Gen

Define your protocols for webservices, protobuf, Avro, etc., in one place, and automatically:

- Generate protocol schemas for Avro, Protobuf, JSON, and other systems.
- CI Testing which validates that:
    - Protocol and schema definitions are valid.
    - Example data matches its schema.
    - etc.
- Generate source code for integration with your favorite languages.
- Example python code for processing messages using the schema definitions.

The main readme for the installable python package is [dist-readme.md](dist-readme.md).

## Generated Documenation

An example of the markdown documentation is generated by the [generate.py](interface_gen/generate.py) script:

[docs/generated](docs/generated/index.md)

## Definitions

| Term | Definition |
| --- | --- |
| Avro | [Apache Avro](http://https://avro.apache.org/) is a data serialization system which is widely used in open-source "big data" systems. We currently just use it's [definition language](https://avro.apache.org/docs/1.11.1/idl-language/) as a convenient way to specify object types we exchange when using our API. | 
| Avro IDL | A more ergonomic format for describing Avro Schemas. The IDL text can be automatically converted to the [Avro Schema JSON](https://avro.apache.org/docs/1.11.1/specification/) format, which is the primary format used by Avro tools, but is harder to read and type. |
| codegen | "Code generation" is the process of running a program which automatically generates source code for another program. The input to a code generator is typically a text file written in an IDL format. |
| encoding | An encoding describes how to translate from a *protocol* to actual data bytes to be sent to or received from a service. |
| endpoint | An API *endpoint* describes the location of a service or API which you will send to or receive from. If the API is a web service, for example, the endpoint is a URI such as `http://someservice.org:9999/api/v1/stuff`. If the API is a function call into a software library, the endpoint would be which module and function to call, and so on. |
| IDL | Interface Definition Language. This is a specific format (syntax) of text used to describe the structure and types of data being passed between systems. Some examples are [proto 3](https://protobuf.dev/programming-guides/proto3/), [OpenAPI (OAS)](https://swagger.io/specification/), [ASN.1](https://en.wikipedia.org/wiki/ASN.1), [FlatBuffers Schema (FBS)](https://flatbuffers.dev/flatbuffers_guide_writing_schema.html), and [many more](https://en.wikipedia.org/wiki/Interface_description_language). |
| protocol | In this context, we use "protocol" to describe the ***logical*** format of the messages passed over an API endpoint. For example, an API endpoint may take a single number as a parameter. How that number is actually formated (e.g. on the network), depends on the ***encoding***. |


### Continuous Integration

Automated tests which run in CI (Github actions) validate the definitions by
(1) parsing the schema definition file, and ensuring it is valid, and (2)
loading the example data with that schema, verifying that the sample data
matches the defined format (schema).

### Message Types (Schema) and Example Data

Each version of the protocol specification has its own folder in both the
`example_data` and the `protocol` directories. The format of the version folder
is `v<version>`.

*Protocol* definitions are written in
[Avro IDL](https://avro.apache.org/docs/1.11.1/specification/) format in a file
named `<protocol>.avdl`. This is the main human-edited definition for all our
protocol definitions.

Each *protocol* definition contains one or more *message types*. For example,
the [trip.avdl](protocol/v0.1-example/trip.avdl) protocol definition defines
`StartTrip` and `EndTrip` message schemas, as well as defining a common type
`GeomType`, which is used for coordinate fields in both the messages.

### Creating a New Message Type / Protocol

Assume we want to create a new message type definition for a two `hello`
protocol messages called `HelloRequest` and `HelloReply` for protocol spec.
version 2.3. The steps for doing this are:

1. Create a new Avro IDL file `hello.avdl` in the `protocol/v2.3/` directory:

```
protocol Hello {

    /** Hello message used to say Hi. */
    record HelloRequest {

        /** Greeting text. */
        string greeting;

        /** Some number. */
        int favorite_number;
    }

    /** Response message. */
    record HelloResponse {

        /** Any reply you'd like to include. */
        string reply;
    }
}
```

2. Run the schema generation tool to create the target schema files (.avsc, .proto, etc.)
for each type.

Instructions are in [interface_gen/README.md](interface_gen/README.md).

This should create two new files, `protocol/v2.3/schema/HelloRequest.avsc` and
`protocol/v2.3/schema/HelloResponse.avsc`, as well as any other generated
definitions (e.g. `protocol/v2.3/proto3`).

3. Add example data and add a validation step to the python unit tests. Create
two new files `HelloRequest.json` and `HelloResponse.json` in the
`example_data/v2.3/` folder, each containing example data which matches the
defined format.

 Next, modify the unit test in `protocols_test.py` to include a
 validation test of the two new schemas and example data files.

### Generating Protobuf Definitions (proto3)

Protobuf definitions are automatically generated when you run the generation
script described above.

*Note: you can modify the `main()` function in generate.py to customize its behavior.*

This script creates a separate directory `proto3`, adjacent to the `schema`
directory, which contains proto3 definitions for protobuf.

### Publishing this Package

See [publish.md](publish.md) for instructions on how to publish this package to PyPi.

# Interface Specification Version 0.1-example

## Overview

Table of schemas, grouped by protocol:

- [trip (Avro IDL)](#trip) (see also [protobuf](#trip-proto3)):
  - [TripType](/protocol/v0.1-example/schema/TripType.avsc)
  - [GeomType](/protocol/v0.1-example/schema/GeomType.avsc)
  - [TripStart](/protocol/v0.1-example/schema/TripStart.avsc)
  - [TripEnd](/protocol/v0.1-example/schema/TripEnd.avsc)
- [sanity (Avro IDL)](#sanity) (see also [protobuf](#sanity-proto3)):
  - [Sanity](/protocol/v0.1-example/schema/Sanity.avsc)
## Protocols

### trip

See also the [protobuf](#trip-proto3)

```avdl
@namespace("v0.1-example")

/**
 * Example protocol definition for a fitness or hiking app where you that
 * allows you to record the start and end of your trip.
 * Exercise: Add a new file 'waypoint.avdl' that models annotating places
 * along the way.
 */
protocol Trip {

    enum TripType {
        Hiking,
        Biking
    } = Hiking;

    enum GeomType {
        Point,
        Polygon
    } = Point;

    /** Trip start message. */
    record TripStart {
        /** 'trip_start' */
        string name;

        /** Timestamp in ISO 8601 format, UTC */
        string timestamp;

        /*  Could also be: Milliseconds since unix epoch, UTC. */
        /* timestamp_ms timestamp; */

        /** Trip ID, .e.g '06.1.2024'. */
        string trip_id;

        /** Hiking or biking? */
        TripType trip_type;

        /** Number of travellers */
        int num_travellers;

        /** Location where you started. geoJSON geometry type. Typically a
         *  Point but could also be a Polygon. */
        GeomType coord_type;

        /** geoJSON geometry coordinates, 1 element for Point, at least 4
         * points for Polygon. */
        array<array<double>> coordinates;
    }

    /** Trip end message. */
    record TripEnd {
        /** 'trip_end' */
        string name;

        /** Timestamp in ISO 8601 format, UTC */
        string timestamp;

        /** Trip ID, .e.g '06.1.2024'. */
        string trip_id;
    }
}

```

### sanity

See also the [protobuf](#sanity-proto3)

```avdl
@namespace("v0.1-example")
protocol Sanity {

    record Sanity {
        string name;
        int count;
        float realnum;
        array<string> cities;
    }
}


```

## Proto3 Definitions

### trip (proto3)

#### TripType (proto3)

```protobuf
syntax = "proto3";

package v0.1-example;

enum TripType {
  Hiking = 0;
  Biking = 1;
}


```

#### GeomType (proto3)

```protobuf
syntax = "proto3";

package v0.1-example;

enum GeomType {
  Point = 0;
  Polygon = 1;
}


```

#### TripStart (proto3)

```protobuf
syntax = "proto3";

package v0.1-example;

message TripStart {
  string name = 1;
  string timestamp = 2;
  string trip_id = 3;
  TripTypeEnum TripType = 4;
  int32 num_travellers = 5;
  GeomTypeEnum GeomType = 6;
  repeated array coordinates = 7;
  enum TripTypeEnum {
    Hiking = 0;
    Biking = 1;
  }
  enum GeomTypeEnum {
    Point = 0;
    Polygon = 1;
  }
}

```

#### TripEnd (proto3)

```protobuf
syntax = "proto3";

package v0.1-example;

message TripEnd {
  string name = 1;
  string timestamp = 2;
  string trip_id = 3;
}

```

### sanity (proto3)

#### Sanity (proto3)

```protobuf
syntax = "proto3";

package v0.1-example;

message Sanity {
  string name = 1;
  int32 count = 2;
  float realnum = 3;
  repeated string cities = 4;
}

```


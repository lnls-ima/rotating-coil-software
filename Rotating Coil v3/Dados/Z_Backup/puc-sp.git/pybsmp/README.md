#PyBSMP

PyBSMP is a client library for the [Basic Small Messages Protocol (BSMP)](1). As such, it contains functions and methods corresponding to each and every command in the protocol [specification](2). It depends on [pySerial](http://pyserial.sourceforge.net/) to work.

This Python implementation allows very readable and concise code to be written in order to comunicate with a BSMP server.

    import bsmp
    b = bsmp.TCPClient("10.0.0.2", 4000)
    b.update()
    print b.varsList[5].read()

This snippet connects to a BSMP server at the specified address, reads its entities lists and prints the value of the variable with id 5.

    c = b.curvesList[2]
    c.write([i & 0xFF for i in range(c.size)])

The previous snippet writes a pattern to the curve with id 2.


## Importing the library

Simply:

    import bsmp

Or if the library resides on a custom directory:

    import sys
    sys.path.append("/path/to/bsmp")
    import bsmp


## Creating an instance

PyBSMP provides three types of instances, each using a specific type of communication. All of their constructors have the same two last parameters: 

- `retries`: the number of times to retry a message before throwing an exception (default `3`);
- `debug`: if enabled prints raw requests and responses to the standard error (default `False`).

### Raw Client

    bsmp.Client(sendFunction, recvFunction, retries=3, debug=False)

A Raw Client relies on two functions to send/receive bytes. If the messages are to be embedded in another protocol, it's the reponsibility of those functions to properly pack and unpack the outer protocol and deliver only useful data to the library. The messages passed to/returned from those functions must be in the format defined in the 'application' layer of the protocol.

- `sendFunction`: a function that takes a list of `int`'s to be sent and send them (values in the range of a C's `unsigned char`);
- `recvFunction`: a function that returns the received bytes of a message in the form of a list of `int`'s.


### TCP Client

    bsmp.TCPClient(ip, port, retries=3, debug=False)

A TCP Client automatically opens a TCP socket and communicates directly with the server. The messages exchanged are in the format defined in the 'application' layer of the protocol.

- `ip`: IP of the server;
- `port`: number of the TCP port the server is listening to.

_Example:_

    b = bsmp.TCPClient("10.0.0.2", 4000)

### Serial Client

    bsmp.SerialClient(serPort, serBaud, serAddress, retries=3, debug=False)

The Serial Client opens a serial port and assumes exclusive access to it. It builds messages using both 'transport' and 'application' layers defined in the specification.

- `serPort`: name of the serial port
- `serBaud`: baudrate (in bps) of the port
- `serAddress`: address of the server in the serial network

_Example:_

    b = bsmp.SerialClient("/dev/ttyS0", 57600, 5)

## Instance attributes

An instance of this library stores inside it five attributes that are initially set to `None`. Those attributes can be selectively updated with `query*()` methods or all at once with the `update()` method, all described in this section.

- `version`: Version of the protocol the server communicates with.
- `varsList`: list of Variables in the server.
- `groupsList`: list of Groups in the server.
- `curvesList`: list of Curves in the server.
- `funcsList`: list of Functions in the server.

They _can_ be accessed directly, like `b.version`, but it is **highly recommended** that they be accessed via `query*()` methods.

All `query*()` methods communicate with the server only if the `force` argument is `True` or if the underlying instance attribute is `None`. Otherwise those methods will return the values stored in the corresponding attribute.

### `update()`

Updates all instance attributes of the instance.

_Example:_

    b.update()

### `queryVersion(force=False)`

Corresponds to the **Query Version (0x00)** BSMP command. Returns a `Version`, which contains the attributes `version`, `subversion` and `revision`, as per specification.

_Example:_

    v = b.queryVersion()
    print("Server Version: {} Subversion: {}".format((v.version,v.subversion))

A `Version` object can be printed directly:

_Example:_

    print(b.queryVersion()) # Prints "2.00.000", for example

### `queryVarsList(force=False)`

Corresponds to the **Query List of Variables (0x02)** BSMP command. Returns a list of `Variable` objects present in the server, each of which can be manipulated using the methods described in the "`Variable` object" section.

### `queryGroupsList(force=False)`

Corresponds to the **Query List of Groups (0x04)** and the `Query Group (0x06)` BSMP commands. Returns a list of `Group` objects present in the server, each of which can be manipulated using the methods described in the "`Group` object" section.

### `queryCurvesList(force=False)`

Corresponds to the **Query List of Curves (0x08)** BSMP command. Returns a list of `Curve` objects present in the server, each of which can be manipulated using the methods described in the "`Curve` object" section.

### `queryFunctionsList(force=False)`

Corresponds to the **Query List of Functions (0x0C)** BSMP command. Returns a list of `Function` objects present in the server, each of which can be manipulated using the methods described in the "`Function` object" section.

### `groupCreate(variables)`

Corresponds to the **Create Group of Variables (0x30)** BSMP command. `variables` must be a list with `Variable` objects from the list returned by `queryVarsList()` method.

_Example:_

Create a Group with a single Variable: the first one.

    b = bsmp.Client(...)
    vars = b.queryVarsList()
    if not vars:
        print("There are no Variables in the server")
        exit(0)
    b.groupCreate([vars[0]])


### `groupRemoveAll()`

Corresponds to the **Remove all Groups of Variables (0x32)** BSMP command. It  erases all groups created by the `groupCreate` method.

## `Variable` object

A `Variable` object contains the `id`, `writable` and `size` attributes, corresponding to their counterparts in the protocol specificaton.

Its methods are:

### `read()`

Corresponds to the **Read Variable (0x10)** BSMP command. Returns a list of integers with length equal to the Variable's `size` attribute. This list is the **value** of the `Variable`.

### `write(value)`

Corresponds to the **Write Variable (0x20)** BSMP command. `value` must be a list of integers (range 0 ~ 255) with length equal to the Variable's `size` attribute.

### `writeAndRead(value, readVar)`

Corresponds to the **Write And Read Variables (0x28)** BSMP command. `value` must be a list of integers (range 0 ~ 255) with length equal to the Variable's `size` attribute. `readVar` must be a valid `Variable` object.

### Bitwise operations

Corresponds to the **Binary operation on a Variable (0x24)** BSMP command. The methods are:

- `bitwiseAND(mask)`
- `bitwiseOR(mask)`
- `bitwiseXOR(mask)`
- `bitwiseSET(mask)`
- `bitwiseCLEAR(mask)`
- `bitwiseTOGGLE(mask)`

All of them expect `mask` to be a list of integers (inside the range 0 ~ 255) of length equal to the Variable's `size` attribute.

## `Group` object

A `Group` object contains the `id`, `writable` and `size` attributes, corresponding to their counterparts in the protocol specificaton. It also contains a list of its Variables, the `vars` attribute.

Its methods are:

### `read()`

Corresponds to the **Read Group (0x12)** BSMP command. Returns a list of integers with length equal to the Group's `size` attribute. This list is the concatenation of all **values** of the Group's Variables.

### `write(groupedValues)`

Corresponds to the **Write Group (0x22)** BSMP command. `value` must be a list of integers (range 0 ~ 255) with length equal to the Group's `size` attribute.

### Bitwise operations

Corresponds to the **Binary operation on a Group (0x26)** BSMP command. The methods are:

- `bitwiseAND(mask)`
- `bitwiseOR(mask)`
- `bitwiseXOR(mask)`
- `bitwiseSET(mask)`
- `bitwiseCLEAR(mask)`
- `bitwiseTOGGLE(mask)`

All of them expect `mask` to be a list of integers (inside the range 0 ~ 255) of length equal to the Group's `size` attribute.

## `Curve` object

A `Curve` object contains the `id`, `writable`, `nBlocks`, `blockSize` and `cSum` attributes, corresponding to their counterparts in the protocol specificaton. It also contains a `size` attribute, which is the product of `nBlocks` by `blockSize`.

Its methods are:

### `readBlock(blockNumber)`

Corresponds to the **Request Curve Block (0x40)** BSMP command. `blockNumber` must be in the range 0 ~ (`nBlocks`-1). A list of integers (range 0 ~ 255) with length up to the Curve's `blockSize` attribute is returned.

### `read()`

This is a helper method that calls the `readBlock` method up to `nBlocks` times (i.e. reads the entire Curve). It returns a list with up to `size` integers, which is the concatenation of all lists returned by each `readBlock` call.

### `writeBlock(blockNumber, blockData)`

Corresponds to the **Curve Block (0x41)** BSMP command. `blockNumber` must be in the range 0 ~ (`nBlocks`-1). `blockData` must be a list of integers (range 0 ~ 255) with length up to the Curve's `blockSize` attribute.

### `write(data, force = False)`

Like `read()`, this method is a helper. It writes values to the entire Curve. `data` must be a list of integers in the range 0~255 with up to `size` elements. This helper calculates the MD5 checksum of the `data` argument and doesn't send the data if the calculated checksum matches the checksum reported by the server, **unless** `force` is `True`. After sending all the blocks, the `recalcCSum` method is called.

_Example:_

Writes the byte `0xAA` to all values of the first `writable` Curve of a server.

    b = bsmp.Client(...)
    wrCurves = [c for c in b.queryCurvesList() if c.writable]
    if not wrCurves:
       print("No writable curves found")
       exit(0)
    c = wrCurves[0]
    c.write([0xAA]*c.size, True)

### `recalcCSum()`

Corresponds to the **Recalculate Curve Checksum (0x42)** BSMP command. The `cSum` property is updated with the string version of the MD5 checksum of the curve, calculated by the server. This same string is returned.

## `Function` object

A `Function` object contains the `id`, `input` and `output` attributes, corresponding to their counterparts in the protocol specificaton. It contains only one method, `execute`.

### `execute(inputData = [])`

Corresponds to the **Execute Function (0x50)** BSMP command. `inputData` must be a list with integers in the range 0~255 and length equal to the `input` attribute. It returns a tuple with two elements. The first element is the return code, the second one is the result of the execution. If the return code is `CMD_FUNCTION_RETURN`, the execution data will be a list with `output` integers in the range 0~255. Otherwise, if the return code is `CMD_FUNCTION_ERROR`, the second element will then be a list with a single integer, which is the error code.

_Example:_

Execute the first available function with all zeros input.

    b = bsmp.Client(...)
    funcs = b.queryFuncsList()
    if not funcs:
        print("No Functions in the server")
        exit(0)
    f = funcs[0]
    resultCode, resultData = f.execute([0]*f.input)
    if resultCode == bsmp.CMD_FUNCTION_RETURN:
        print("Function executed successfully. Returned data:")
        print(resultData)
    else:
        print("Function returned an error. Error code: {}".format(resultData[0]))




[1]: (http://github.com/brunoseivam/libbsmp)
[2]: (http://github.com/brunoseivam/libbsmp/blob/master/doc/protocol_v2.00_pt_BR.pdf)

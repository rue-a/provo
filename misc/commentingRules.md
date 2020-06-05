# Rules for provenance annotations in scripts

Serialization of provenance of scripted workflows according to PROV-O via schematized comments.

*Examples in this document are written in Python, single line comments are indicated with '**#**'.*

It is assumed that a workflow consists of chained ***input -> process -> output*** - units (IPO-Unit), where the output of one process can be the input of another one.

Every provenance annotation begins with @prov followed by a dot, a keyword and an according statement: 

```python
# @prov.keyword ...
```

Any immediately following single line comments are attached to the statement:
```python
# @prov.keyword ... very ...
# ... long ... statement

# an empty line or a new '@prov' stops the annotation
```

## Setup

Before the annotation of the first ***input -> process -> output*** - unit, the script needs to be set up with:

```python
# @prov.init
```

This can be followed up with optional commands concerning the author of the script:


```python
# @prov.author Arne
# @prov.organization TU Dresden
```

## Adding IPO-units

An annotation for a IPO-unit is structured as follows:
```python
# @prov.unit out1, out2, ... = process(in1, in2, ...) processtype
```

A given IPO-unit can have any number of inputs and outputs. A particular input or output can be any data. In the context of scripted workflows, such data typically refers to a variable in the script. The process on the other hand resembles a function (self-written or package related).

It is recommended to use the same variable and function names as in the script. The optional appending of labels and descriptions is described further below.

If the output of a given IPO-unit is also the input of another IPO-unit, it needs the have the same name in the annotation! A simple example with a process that adds two numbers and has their sum as output looks as follows:

```python
# @prov.init
# @prov.author Arne
# @prov.organization TU Dresden

def addNumbers(num1, num2):
    return num1 + num2

a = 5
b = 2

# @prov.unit c = addNumbers(a,b) valueChange
c = addNumbers(a, b)

# @prov.unit d = addNumbers(c, a) valueChange
d = addNumbers(c, a)
```

> ich koennte das @prov.unit statement auch so implementieren, dass fuer den Fall das nur der process type angegeben wird, die darauf folgende Zeile als IPO-unit gelesen wird. So wie ich mir das vorstelle, sollten die oft identisch sein. Das wird aber natuerlich nicht immer zutreffen:

```python
# @prov.unit valueChange
c = addNumbers(a, b)
```

If you don't define functions for everything, you can of cause use any name for the items of the IPO-unit:

```python
def addNumbers(num1, num2):
    return num1 + num2

a = 5
b = 2

# @prov.unit c = multiplyNumbers(b, a) valueChange
c = 0
i = 0
while i < a:
    c = c + b
    i += 1
```

## Labels and descriptions

Any item of an IPO-unit can be enriched with a label and a description. This can happen at any point of the document, even before the item is "used":

```python
# @prov.label itemName label
# @prov.description itemName description
```

With the example from above:

```python

# @prov.label a 5
# @prov.label b 2
# @prov.description b The number 2.

def addNumbers(num1, num2):
    # @prov.description addNumbers Adds two numbers.
    return num1 + num2

a = 5
b = 2

# @prov.unit c = multiplyNumbers(b, a) valueChange
c = 0
i = 0
while i < a:
    c = addNumbers(c, b)
    i += 1

# prov.description multiplyNumbers Multiplies two numbers.
```

## Multi-file-scripts

If your script is distributed over multiple files you can link to file via:

```python
# @prov.linkFile relativePath
```

This can e.g. be the case if all your function are defined in a separate file. It would make sense to add the description directly there. If you link multiple files, remember that all item names need to match those from the main-file:

```python
# @prov.init
# @prov.author Arne
# @prov.organization TU Dresden

# prov.linkFile ./exampleMethods.py

a = 5
b = 2

# @prov.unit c = addNumbers(a,b) valueChange
c = add(a, b)
```

```python
''' exampleMethods.py '''

def add(num1, num2):
    # @prov.description addNumbers Adds two Numbers.
    return num1 + num2

def sub(num1, num2):
    return num1 - num2
```
## Financial Literacy Game

Installing the package:

```sh
poetry install
```

Entering the virtual environment:

```sh
$(poetry env activate)
```

> You need to activate the virtual environment before running the server.

Running the server in production mode:

```sh
qs run
```

Running the server in debug mode:

```sh
QS_DEBUG=1 qs run
```

Generate TypeScript specs:

```sh
qs schema typescript
```

> The output is going to be available at `/api-specs.ts`.

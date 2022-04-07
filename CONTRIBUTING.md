# Contributing to `dominion-game`

Thanks for deciding to contribute! This project is still in its early stages and could use your help!

## Code of Conduct

This repository and anyone contributing to it is governed by this [Code of Conduct](https://github.com/eshapiro42/dominion-game/blob/main/CODE_OF_CONDUCT.md).

By contributing, you are agreeing to uphold this code and to do no harm to the repository or any of its users or contributors. Please report unacceptable behavior by opening an issue.

## Technologies Used

The backend of this project is written in `Python` and uses [`Flask-SocketIO`](https://flask-socketio.readthedocs.io/en/latest/) as a server. Backend code is located in the root of the repository and in the `dominion` subdirectory.

The frontend is written in [`Svelte.js`](https://svelte.dev/docs). Note that `Svelte` code requires compilation in order to be run. Frontend code is located in the root of the repository and in the `client` subdirectory.

View the [readme](https://github.com/eshapiro42/dominion-game/blob/svelte_client/README.md) on the `svelte_client` branch for tips on getting up and running.

## What Should I Know Before I Jump In?

First and foremost, I'm not a frontend developer so don't judge me too harshly because my frontend code is messy. One of my long-term goals is to clean it up and add proper documentation, but help on this front is greatly appreciated!

Active development is based off of the `svelte_client` branch of this repository. All pull requests should be made against that branch until the [first milestone](https://github.com/eshapiro42/dominion-game/milestone/1) is reached.

## Pull Requests and Style Guidelines

All contributions to this repository should maintain (or ideally improve) the existing quality and organization of the project and its codebase.

Once you are satisfied that the feature you are adding or issue you are resolving is fully working and in a good state, open a pull request against the `svelte_client` branch of this repository. Pull requests are expected to adhere to the following style guidelines.

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.

### Git Commits

* Commits should be as small and self-contained as possible while still adding meaningful functionality to the project. Do not combine two unrelated changes into one commit.

### Git Commit Messages

* Use the present tense ("Add feature", not "Added feature").
* Use the imperative mood ("Move cursor to", not "Moves cursor to").
* Try to limit the first line to 72 characters or less. A little bit over is fine.
* Reference issues and pull requests liberally after the first line.

### Python Style Guidelines

* Adhere to [PEP 8](https://peps.python.org/pep-0008/), with the exception of maximum line length; that should be roughly 120 characters.
* **All indentations should be exactly four spaces.** Tabs should not be used under any circumstances.
* Comments and docstrings should be used liberally for clarification but should not take up too much screen space.
* `snake_case` should be used for all names.
* Function and variable names should be informative but brief, and should be as consistent as possible with the existing code.
* Code should be as modular as possible, and new code should try to have no impact on the existing code (except bug fixes of course). Try to keep new code in a separate file when sensible.

### Svelte Style Guidelines
* Comments should be used liberally for clarification but should not take up too much screen space.
* `camelCase` should be used for all names, with the exception of `JSON` keys that come from the backend.
* Code should be as modular as possible, and new code should try to have no impact on the existing code (except bug fixes of course). Try to create a new component for new code when sensible.

## License

By contributing to the `dominion-game` repository, you agree that your contributions will be licensed under its [MIT License](https://github.com/eshapiro42/dominion-game/blob/main/LICENSE).

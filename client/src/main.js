import App from './App.svelte';

const app = new App({
	target: document.body,
	props: {
		socket: io.connect(),
	}
});

export default app;
import {
    readable,
    writable
} from "svelte/store";

export let socket = readable(io.connect());

export let currentPlayer = writable("");
export let room = writable(null);
export let username = writable("");
export let activeCarousel = writable(null);
export let chosenFont = writable(null);

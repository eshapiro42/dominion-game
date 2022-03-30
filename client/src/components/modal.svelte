<script>
    import App from "../App.svelte";
import Card from "./card.svelte";

    export let show = false;

    let card = {
        name: "Copper",
        effects: [""],
        description: "",
        cost: 0,
        type: "Treasure",
        id: -1,
    }
</script>

{#if show}
    <main
        on:click|self
    >
        <div class="contents">
            <slot name="contents">
                <span class="missing"></span>
            </slot>
        </div>
    </main>
{/if}

<style>
    main {
        width: 100%;
        height: 100%;
        left: 0;
        top: 0;
        display: flex;
        position: fixed;
        background-color: rgba(0, 0, 0, 0.7);
        text-align: center;
        z-index: 10;
    }

    .contents {
        justify-content: center;
        align-items: center;
        margin: auto;
    }
</style>
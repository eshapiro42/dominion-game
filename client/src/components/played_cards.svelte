<script>
    import CardCarousel from "./card_carousel.svelte";

    export let socket;
    export let gameStarted;
    let waitingForSelection = false;

    let cards = [];

    socket.on(
        "display played cards", 
        (data) => {
            cards = data.cards;
        },
    );
</script>

{#if gameStarted}
    <main>
        <CardCarousel
            title="Played Cards"
            {waitingForSelection}
            {cards}
        />
    </main>
{/if}

<style>
</style>
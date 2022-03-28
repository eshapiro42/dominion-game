<script>
    import CardCarousel from "./card_carousel.svelte";

    export let socket;
    export let gameStarted;

    let cards = [];


    socket.on(
        "display hand", 
        (data) => {
            cards = data.cards;
        },
    );
</script>

{#if gameStarted}
    <main>
        <CardCarousel
            title="Your Hand"
            {cards}
        />
    </main>
{/if}

<style>
    
</style>
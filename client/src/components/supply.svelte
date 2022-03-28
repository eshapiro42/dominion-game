<script>
    import CardCarousel from "./card_carousel.svelte";

    export let socket;
    export let gameStarted;

    let cards = [];


    socket.on(
        "display supply", 
        (data) => {
            console.log(data.cards);
            cards = data.cards;
        },
    );
</script>

{#if gameStarted}
    <main>
        <CardCarousel
            title="Supply"
            {cards}
        />
    </main>
{/if}

<style>
    
</style>
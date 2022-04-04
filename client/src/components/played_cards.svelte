<script>
    import CardCarousel from "./card_carousel.svelte";

    export let socket;
    export let gameStarted;
    export let currentPlayer;

    let waitingForSelection = false;

    let cards = [];

    socket.on(
        "display played cards", 
        (data) => {
            cards = data.cards;
        },
    );

    socket.on(
        "current player",
        (data) => {
            currentPlayer = data;
        },
    )

    $: currentPlayerName = currentPlayer == null ? "No One" : currentPlayer;

</script>

{#if gameStarted}
    <main>
        <CardCarousel
            title="{currentPlayerName}'s Played Cards"
            sortByProperty = "orderSent"
            {waitingForSelection}
            {cards}
        />
    </main>
{/if}

<style>
</style>
<script>
    import {
        socket,
        currentPlayer,
    } from "../stores.js";

    import CardCarousel from "./card_carousel.svelte";

    let waitingForSelection = false;

    let cards = [];

    $socket.on(
        "display played cards", 
        (data) => {
            cards = data.cards;
        },
    );

    $socket.on(
        "current player",
        (data) => {
            $currentPlayer = data;
        },
    )
</script>

<section id="Played Cards">
    <main>
        <CardCarousel
            title="{$currentPlayer == "" ? "No One" : $currentPlayer}'s Played Cards"
            sortByProperty = "orderSent"
            {waitingForSelection}
            {cards}
        />
    </main>
</section>

<style>
</style>
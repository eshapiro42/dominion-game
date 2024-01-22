<script>
    import {socket} from "../stores.js";

    let title = "Trade Route";
    let victoryCards = [];
    let tokens = 0;
    let show = false;

    $socket.on(
        "display trade route",
        function(data) {
            show = true;
            victoryCards = data.victory_cards;
            tokens = data.tokens;
        }
    );
</script>

{#if (show)}
    <section id="Trade Route">
        <main class="panel">
            <div class="hoverable">
                <div class="title">
                    <h4>{title}</h4>
                </div>
                <span class="hoverable-text">
                    <span>
                        At the start of the game, there is a Coin token on each Victory card pile being used.
                    </span>
                    <span>
                        Whenever any player gains the first card from a Victory card pile, its Coin token is moved to this mat.     
                    </span>
                </span>
            </div>

            <div class="description">
                <h6>
                </h6>
                <h6>
                </h6>
            </div>

            <div class="columns">
                {#if (victoryCards.length > 0)}
                    <div class="victoryCards">
                        {#each victoryCards as victoryCard}
                            <p>{victoryCard}</p>
                        {/each}
                    </div>
                {/if}

                <div class="coinTokens">
                    <div>
                        {tokens} <i class="bi bi-coin"></i>
                    </div>
                </div>
            </div>
        </main>
    </section>
{/if}

<style>
    main {
        margin-top: 20px;
        border: 1px solid var(--border-color);
    }

    .title {
        width: 100%;
        height: 100%;
        text-align: center;
        margin-top: 25px;
    }

    .columns {
        display: flex;
        flex-direction: row;
        gap: 50px;
        flex-basis: 100%;
        justify-content: space-evenly;
        margin-bottom: 25px;
        padding-top: 25px;
    }

    .victoryCards {
        flex-basis: 50%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        padding-top: 25px;
        margin-left: 10px;
        gap: 10px;
        background-color: var(--thead-background-color);
        border: 1px solid var(--border-color);
    }

    .coinTokens {
        flex-basis: 50%;
        text-align: center;
        font-size: 60px;
        align-self: center;
        padding: 10px;
        margin-right: 10px;
    }
</style>
<script>
    import {socket} from "../stores.js";

    let title = "Player Info";
    let playersInfo = [];

    $socket.on("display players info", function(data) {
        playersInfo = data;
    });
</script>

<section id="Player Info">
    <main class="panel">
        <div class="title">
            <h4>{title}</h4>
        </div>

        <div class="infoContainer">
            {#each playersInfo as playerInfo}
                <div class="playerInfo">
                    <div>
                        <h5>{playerInfo.name}</h5>
                    </div>
                    <div class="playerInfoItem">
                        <div>Hand Size</div>
                        <div>{playerInfo.hand_size}</div>
                    </div>
                    <div class="playerInfoItem">
                        <div>Discard Size</div>
                        <div>{playerInfo.discard_size}</div>
                    </div>
                    <div class="playerInfoItem">
                        <div>Deck Size</div>
                        <div>{playerInfo.deck_size}</div>
                    </div>
                    <div class="playerInfoItem">
                        <div>Played Cards</div>
                        <div>{playerInfo.played_size}</div>
                    </div>
                    <div class="playerInfoItem">
                        <div>Total Cards</div>
                        <div>{playerInfo.total_cards}</div>
                    </div>
                    {#if "victory_tokens" in playerInfo}
                        <div class="playerInfoItem">
                            <div>Victory Tokens</div>
                            <div>{playerInfo.victory_tokens}</div>
                        </div>
                    {/if}
                    {#if "coffers" in playerInfo}
                    <div class="playerInfoItem">
                        <div>Coffers</div>
                        <div>{playerInfo.coffers}</div>
                    </div>
                    {/if}
                </div>
            {/each}
        </div>
    </main>
</section>

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

    .infoContainer {
        flex-basis: 100%;
        flex-wrap: wrap;
        display: flex;
        overflow-x: auto;
        padding-left: 10px;
        padding-right: 10px;
        padding-bottom: 25px;
        padding-top: 25px;
        justify-content: space-around;
        gap: 20px
    }

    .playerInfo {
        display: flex;
        flex-direction: column;
        justify-content: space-evenly;
        gap: 10px;
        padding: 25px;
        border: 1px solid var(--border-color);
        background-color: var(--thead-background-color);
        color: var(--light-text-color);
    }

    .playerInfoItem {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        gap: 20px;
        align-items: center;
    }
</style>
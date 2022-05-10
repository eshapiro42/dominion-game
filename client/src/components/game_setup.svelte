<script>
    import {createEventDispatcher} from "svelte";

    import {
        socket,
        room,
        username,
    } from "../stores.js";

    const dispatch = createEventDispatcher();

    export let roomJoined;
    export let roomCreator;
    
    let gameStartable = false;
    let shown = true;

    var expansions = [
        {name: "Dominion", property: "dominion", selected: false},
        {name: "Intrigue", property: "intrigue", selected: false},
        {name: "Prosperity", property: "prosperity", selected: false},
        {name: "Cornucopia", property: "cornucopia", selected: false},
    ]

    var supplyCustomizations = [
        {
            name: "Allow simultaneous reactions",
            property: "allowSimultaneousReactions",
            selected: false,
            description: [
                "Allow attacked players to react to an Attack (or certain Actions) simultaneously and asynchronously (when doing so is sensible).",
                "This only works for Attack effects where the only required input is from the players being attacked, such as with the Militia. If the Attack requires feedback from the attacker, like with the Thief, the frontend is not currently equipped to deal with simultaneous reactions.",
                "This also cannot be used for Attacks that require the attacked players to gain cards from the Supply, such as the Witch. That's because there may be only one of a given card left in the Supply, and therefore the effect must be resolved in turn order.",
                "<b>Supported cards</b>: Bandit, Bishop, Bureaucrat, Fortune Teller, Goons, Masquerade, Militia, Minion, Rabble, Tournament, Vault.",
                "<b>Unsupported cards</b>: Followers, Mountebank, Jester, Replace, Spy, Swindler, Thief, Torturer, Witch, Young Witch.",
            ],
        },
        {
            name: "Distribute cost",
            property: "distributeCost", 
            selected: false,
            description: [
                "Attempts to ensure that there are at least two Kingdom cards each in the Supply of cost 2, 3, 4 and 5.",
                "<b>Note</b>: This is not always possible. For instance, the Prosperity expansion does not include any cards of cost 2 and so if it is the only selected expansion this obviously cannot be accomplished.",
            ],
        },
        {
            name: "Disable Attacks",
            property: "disableAttacks", 
            selected: false,
            description: [
                "Do not allow attack cards in the Supply.",
            ],
        },
        {
            name: "Require +2 Action",
            property: "requirePlusTwoAction", 
            selected: false,
            description: [
                "Require that at least one card in the Supply gives +2 Actions or more.",
            ],
        },
        {
            name: "Require +1 Card",
            property: "requireDrawer", 
            selected: false,
            description: [
                "Require that at least one card in the Supply gives +1 Card or more.",
            ],
        },
        {
            name: "Require +1 Buy",
            property: "requireBuy", 
            selected: false,
            description: [
                "Require that at least one card in the Supply gives +1 Buy or more.",
            ],
        },
        {
            name: "Require Trashing",
            property: "requireTrashing", 
            selected: false,
            description: [
                "Require that at least one card in the Supply allows trashing.",
                "This is currently implemented by searching for cards with the word 'trash' in their description. This may not be a totally accurate method.",
            ],
        },
    ]

    function addCPU() {
        $socket.emit("add cpu", {room: $room});
    }


    function startGame() {
        if (!gameStartable) {
            alert("The game cannot be started without at least two players.");
        }
        else if (!expansions.some((expansion) => expansion.selected)) {
            alert("You must select at least one expansion.");
        }           
        else {
            var gameProperties = {
                username: $username,
                room: $room,
            };
            expansions.forEach(
                (expansion) => {
                    gameProperties[expansion.property] = expansion.selected;
                }
            );
            supplyCustomizations.forEach(
                (customization) => {
                    gameProperties[customization.property] = customization.selected;
                }
            );
            $socket.emit(
                "start game",
                gameProperties
            );
            dispatch("started");
            shown = false;
        }
    }

    $socket.on("game startable", function(data) {
        gameStartable = true;
    });

    $socket.on("game started", function(data) {
        dispatch("started");
        shown = false;
    })
</script>

{#if shown}
    {#if roomJoined && roomCreator}
        <main>
            <div class="buttons">
                <button type="button" on:click={startGame} class="btn btn-primary btn-lg btn-block">Start Game</button>
                <button type="button" on:click={addCPU} class="btn btn-secondary btn-lg btn-block">Add CPU</button>
            </div>
            <div class="customizations">
                {#each expansions as expansion}
                    <label class="customization">
                        <input type="checkbox" bind:checked={expansion.selected}>
                        {expansion.name} Expansion
                    </label>
                {/each}
            </div>
            <div class="customizations">
                {#each supplyCustomizations as customization}
                    <label class="customization">
                        <input type="checkbox" bind:checked={customization.selected}>
                        <div class="hoverable">
                            {customization.name}
                            <span class="hoverable-text">
                                {#each customization.description as line}
                                    <span class="hoverable-text-line">
                                        {@html line}
                                    </span>
                                {/each}
                            </span>
                        </div>
                    </label>
                {/each}
            </div>
        </main>
    {:else if roomJoined}
        <main>
            <div>
                <p>Please wait for the host to start the game.</p>
            </div>
        </main>
    {/if}
{/if}

<style>
    main {
        margin-top: 50px;
        display: flex;
        flex-direction: row;
        justify-content: space-evenly;
        flex-wrap: wrap;
    }

    .buttons {
        flex-basis: 100%;
        margin-bottom: 50px;
    }

    .customization {
        padding: 10px;
    }

    .customizations {
        text-align: left;
    }

    .hoverable {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted #343338;
    }

    .hoverable .hoverable-text {
        visibility: hidden;
        position: absolute;
        left: 50px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 10px;
        z-index: 1;
        font-size: 85%;
        width: 300px;
        background-color: #343338;
        color: #dadada;
        text-align: left;
        overflow-wrap: break-word;
        border-radius: 10px;
        padding: 10px;
    }

    .hoverable:hover .hoverable-text {
        visibility: visible;
    }
</style>
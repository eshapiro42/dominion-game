<script>
    import {createEventDispatcher} from "svelte";

    import {
        socket,
        room,
        username,
    } from "../stores.js";

    import CustomKingdomSetup from "./custom_kingdom_setup.svelte";
    import RecommendedKingdomSetup from "./recommended_kingdom_setup.svelte";
    import Tabs from "./tabs.svelte";

    const dispatch = createEventDispatcher();

    export let roomJoined;
    export let roomCreator;
    
    let playersInRoom = [];
    let gameStartable = false;
    let selectedTab;
    let recommendedSets = [];
    let recommendedSet = null;
    let allKingdomCards = [];
    let hidden = false;
    let saved_kingdom = {}
    let customKingdomData = {};
    let openFileOptions = {
        multiple: false,
        types: [
            {
                description: "JSON Files",
                accept: {
                    "application/json": [".json"],
                }
            }
        ]
    };

    var expansions = [
        {name: "Dominion", property: "dominion", selected: false},
        {name: "Intrigue", property: "intrigue", selected: false},
        {name: "Prosperity", property: "prosperity", selected: false},
        {name: "Cornucopia", property: "cornucopia", selected: false},
        {name: "Hinterlands", property: "hinterlands", selected: false},
        {name: "Guilds", property: "guilds", selected: false},
    ];

    var supplyCustomizations = [
        // This does not currently work with only the Cornucopia expansion selected
        // because there might not be enough remaining cards in the Supply of cost
        // 2 or 3.
        // {
        //     name: "Distribute cost",
        //     property: "distributeCost", 
        //     selected: false,
        //     description: [
        //         "Attempts to ensure that there are at least two Kingdom cards each in the Supply of cost 2, 3, 4 and 5.",
        //         "<b>Note</b>: This is not always possible. For instance, the Prosperity expansion does not include any cards of cost 2 and so if it is the only selected expansion this obviously cannot be accomplished.",
        //     ],
        // },
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
    ];

    var allowSimultaneousReactions = {
        name: "Allow simultaneous reactions",
        property: "allowSimultaneousReactions",
        selected: false,
        description: [
            "Allow attacked players to react to an Attack (or certain Actions) simultaneously and asynchronously (when doing so is sensible).",
            "This only works for Attack effects where the only required input is from the players being attacked, such as with the Militia. If the Attack requires feedback from the attacker, like with the Thief, the frontend is not currently equipped to deal with simultaneous reactions.",
            "This also cannot be used for Attacks that require the attacked players to gain cards from the Supply, such as the Witch. That's because there may be only one of a given card left in the Supply, and therefore the effect must be resolved in turn order.",
            "<b>Supported cards</b>: Bandit, Bishop, Bureaucrat, Duchess, Fool's Gold, Fortune Teller, Goons, Margrave, Masquerade, Militia, Minion, Rabble, Taxman, Tournament, Vault.",
            "<b>Unsupported cards</b>: Followers, Mountebank, Noble Brigand, Jester, Oracle, Replace, Soothsayer, Spy, Swindler, Thief, Torturer, Witch, Young Witch.",
        ],
    };

    function addCPU() {
        $socket.emit("add cpu", {room: $room});
    }

    function startGame() {
        if (!gameStartable) {
            alert("The game cannot be started without at least two players.");
            return;
        }
        else if (selectedTab == "Random Kingdom" && !expansions.some((expansion) => expansion.selected)) {
            alert("You must select at least one expansion.");
            return;
        }
        else if (selectedTab == "Recommended Kingdom" && recommendedSet == null) {
            alert("You must select a Recommended Kingdom.");
            return;
        }
        else if (selectedTab == "Custom Kingdom" && customKingdomData["cards"].length !== 10) {
            alert("You must select exactly ten cards (excluding Bane cards).");
            return;
        }
        else if (selectedTab == "Saved Kingdom" && saved_kingdom["data"]["cards"].length !== 10) {
            alert("The loaded Saved Kingdom must contain exactly ten cards (excluding Bane cards).");
            return;
        }
        var gameProperties = {
            username: $username,
            room: $room,
            allowSimultaneousReactions: allowSimultaneousReactions,
        };
        if (selectedTab == "Random Kingdom") {
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
        }
        else if (selectedTab == "Recommended Kingdom") {
            gameProperties["recommended_set_index"] = recommendedSet;
        }
        else if (selectedTab == "Custom Kingdom") {
            gameProperties["custom_set_data"] = customKingdomData;
        }
        else if (selectedTab == "Saved Kingdom") {
            gameProperties["custom_set_data"] = saved_kingdom["data"];
        }
        $socket.emit(
            "start game",
            gameProperties
        );
        dispatch("started");
        hidden = true;
    }

    $socket.on("game startable", function(data) {
        gameStartable = true;
    });

    $socket.on("game started", function(data) {
        dispatch("started");
        hidden = true;
    });

    $socket.on("recommended sets", function(data) {
        recommendedSets = data;
        recommendedSets.forEach(
            (set) => {
                set.selected = false;
            }
        );
    });

    $socket.on(
        "all kingdom cards", 
        (data) => {
            allKingdomCards = data;
        }
    );

    $socket.on("players in room", function(data) {
        playersInRoom = data;
    });

    $: if (roomJoined) {
        $socket.emit(
            "request recommended sets",
            {
                room: $room,
            }
        );
        $socket.emit(
            "request all kingdom cards",
            {
                room: $room,
            }
        );
    }

    // Saved Kingdom reactive variables
    $: allCardNames = allKingdomCards.flatMap(expansion => expansion.cards).flatMap(card => card.name);
    $: if (saved_kingdom.hasOwnProperty("contents")) {
        try {
            saved_kingdom["data"] = JSON.parse(saved_kingdom["contents"]);
        } catch (error) {
            saved_kingdom = {};
            alert("The provided file is not valid JSON.");
        }
        if (Object.keys(saved_kingdom).length !== 0) {
            if (!saved_kingdom["data"].hasOwnProperty("cards")) {
                saved_kingdom = {};
                alert("The provided file does not contain a 'cards' field.")
            }
            else if (!saved_kingdom["data"].hasOwnProperty("bane_card_name")) {
                saved_kingdom = {};
                alert("The provided file does not contain a 'bane_card_name' field.")
            }
            else if (!saved_kingdom["data"].hasOwnProperty("use_platinum_and_colony")) {
                saved_kingdom = {};
                alert("The provided file does not contain a 'use_platinum_and_colony' field.")
            }
            else {
                allCardNames = allKingdomCards.flatMap(expansion => expansion.cards).flatMap(card => card.name);
                saved_kingdom["data"]["cards"].forEach(
                    (card_name) => {
                        if (!allCardNames.includes(card_name)) {
                            saved_kingdom = {};
                            alert(`The provided file contains an invalid card name: ${card_name}.`);
                        }
                    }
                );
                let bane_card_name = saved_kingdom["data"]["bane_card_name"]
                if (!allCardNames.includes(bane_card_name)) {
                    alert(`The provided file contains an invalid Bane card name: ${bane_card_name}`);
                }
            }
        }
    }
</script>

{#if !hidden}
    {#if roomJoined}
        <div class="container">
            <table class="table table-hover table-center">
                <thead>
                    <tr><td><b>Players in Room</b></td></tr>
                </thead>
                <tbody>
                    {#each playersInRoom as player}
                    <tr><td>{player}</td></tr>
                    {/each}
                </tbody>
            </table>
        </div>
        {#if roomCreator}
            <div class="container">
                <div class="buttons">
                    <button type="button" on:click={startGame} class="btn btn-primary btn-lg btn-block">Start Game</button>
                    <button type="button" on:click={addCPU} class="btn btn-secondary btn-lg btn-block">Add CPU</button>
                </div>
                <main>
                    <div class="customizations">
                        <label class="customization space-below">
                            <input type="checkbox" bind:checked={allowSimultaneousReactions.selected}>
                            <div class="hoverable">
                                Allow Simultaneous Reactions
                                <span class="hoverable-text">
                                    {#each allowSimultaneousReactions.description as line}
                                        <span>
                                            {@html line}
                                        </span>
                                    {/each}
                                </span>
                            </div>
                        </label>
                    </div>
                </main>

                <Tabs
                    tabNames={
                        [
                            "Random Kingdom",
                            "Recommended Kingdom",
                            "Custom Kingdom",
                            "Saved Kingdom",
                        ]
                    }
                    bind:selectedTab={selectedTab}
                />

                {#if selectedTab === "Random Kingdom"}
                    <main>
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
                                                <span>
                                                    {@html line}
                                                </span>
                                            {/each}
                                        </span>
                                    </div>
                                </label>
                            {/each}
                        </div>
                    </main>
                {:else if selectedTab === "Recommended Kingdom"}
                    <main>
                        <RecommendedKingdomSetup 
                            {recommendedSets}
                            bind:recommendedSet={recommendedSet}
                    />
                    </main>
                {:else if selectedTab === "Custom Kingdom"}
                    <main>
                        <CustomKingdomSetup 
                            {allKingdomCards}
                            bind:customKingdomData={customKingdomData}
                        />
                    </main>
                {:else if selectedTab === "Saved Kingdom"}
                    <main>
                        {#if saved_kingdom.hasOwnProperty("file_handle")}
                            Loaded {saved_kingdom["file_handle"].name}.
                        {:else}
                            No file loaded.
                        {/if}
                        <button on:click={
                            async () => {
                                [saved_kingdom["file_handle"]] = await window.showOpenFilePicker(openFileOptions);
                                saved_kingdom["file"] = await saved_kingdom["file_handle"].getFile();
                                saved_kingdom["contents"] = await saved_kingdom["file"].text();
                            }}>
                            Select File
                        </button>
                    </main>
                {/if}
            </div>
        {:else}
            <main>
                <div>
                    <p>Please wait for the host to start the game.</p>
                </div>
            </main>
        {/if}
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
        margin-top: 50px;
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

    .space-below {
        margin-bottom: 50px;
    }

    .table {
        text-align: left;
        vertical-align: middle;
    }

    .table-center {
        text-align: center;
    }

    td {
        padding: 20px;
    }
</style>
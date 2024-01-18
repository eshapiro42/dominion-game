<script>
    import {socket, activeCarousel} from "../stores.js";

    let tradeRoute = false;
    let prizes = false;

    $: sections = [
        {
            title: "Played Cards",
            displayName: "Active",
            visible: true,
        },
        {
            title: "Your Hand",
            displayName: "Hand",
            visible: true,
        },
        {
            title: "Supply",
            displayName: "Supply",
            visible: true,
        },
        {
            title: "Your Discard Pile",
            displayName: "Discard",
            visible: true,
        },
        {
            title: "Trash",
            displayName: "Trash",
            visible: true,
        },
        {
            title: "Trade Route",
            displayName: "Trade Route",
            visible: tradeRoute,
        },
        {
            title: "Prizes",
            displayName: "Prizes",
            visible: prizes,
        },
    ]

    $socket.on(
        "display trade route",
        (_) => {
            tradeRoute = true;
        }
    );

    $socket.on(
        "prizes",
        (_) => {
            prizes = true;
        }
    )
</script>

<main>
    {#each sections as section}
        {#if section.visible}
            <a 
                class="section {section.title == $activeCarousel ? "active" : ""}" 
                href="#{section.title}"
            >
                {section.displayName}
            </a>
        {/if}
    {/each}
    <a class="section" href="#Player Info">Players</a>
</main>

<style>
    main {
        left: 0;
        top: 0;
        width: 64px;
        height: 100%;
        position: fixed;
        background-color: #343338;
        color: #dadada;
        display: flex;
        flex-direction: column;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: space-around;
        align-items: stretch;
    }

    /* Do not show sidebar on mobile devices */
    @media (max-width: 767px) {
        main {
             display: none;
        }
    }

    .section {
        justify-content: center;
        align-items: center;
        display: flex;
        writing-mode: vertical-lr;
        transform: rotate(180deg);
        font-weight: bold;
        flex-grow: 1;
        font-size: 20px;
    }

    .section.active {
        background-color: #4f4141;
    }

    .section:hover {
        background-color: #605e67;
    }

    a {
        color: #dadada;
    }

    a:hover {
        text-decoration: none;
    }
</style>
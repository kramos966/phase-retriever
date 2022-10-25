from phase_retriever import PhaseRetriever
import numpy as np
import matplotlib.pyplot as plt
OK = "\033[0;32mOK\033[0;0m"
FAIL = "\033[91mFAIL\033[0;0m"

def test_basics():
    success = True
    retriever = PhaseRetriever()
    pixel_size = 0.0469e-3
    lamb = 520e-6
    M = 1
    p_eff = pixel_size/M/lamb

    # Load dataset
    print("Dataset load... ", end="")
    try:
        retriever.load_dataset("sims")
        print(OK)
    except:
        print(FAIL)

    print("Pixel size set... ", end="")
    try:
        retriever.config(pixel_size=pixel_size)
        retriever.config(lamb=lamb)
        if retriever.options["pixel_size"] != pixel_size:
            raise ValueError()
        print(OK)
    except:
        print(FAIL, f"Expected {0.1} and got{retriever.config[pixel_size]}")

    print("Wavelength set... ", end="")
    try:
        retriever.config(lamb=lamb)
        if retriever.options["pixel_size"] != pixel_size:
            raise ValueError()
        print(OK)
    except:
        print(FAIL, f"Expected {0.1} and got{retriever.config[pixel_size]}")

    print("Window centering... ", end="")
    try:
        retriever.center_window()
        print(OK)
    except:
        print(FAIL)

    print("Phase origin selection... ", end="")
    try:
        retriever.select_phase_origin()
        print(OK)
    except:
        print(FAIL)

    print("Bandiwdth determination... ", end="")
    try:
        retriever.compute_bandwidth(tol=4e-6)
        print(OK)
    except:
        print(FAIL)
    for option in retriever.options:
        print(option, retriever.options[option])

    Ax, Ay = retriever.retrieve()

    ephi_x, ephi_y = retriever.get_phases()

    data = np.load("sims_retrieved/phases.npz")
    cmap = "twilight_shifted"
    fig, ax = plt.subplots(2, 3, constrained_layout=True)
    ax[0, 1].imshow(np.angle(ephi_x), cmap=cmap)
    ax[0, 2].imshow(np.angle(data["phi_x"]), cmap=cmap)
    ax[1, 1].imshow(np.angle(ephi_y), cmap=cmap)
    ax[1, 2].imshow(np.angle(data["phi_y"]), cmap=cmap)

    ax[0, 0].imshow(Ax[0], cmap="gray")
    ax[1, 0].imshow(Ay[0], cmap="gray")

    ax[0, 1].set_title("This program")
    ax[0, 2].set_title("GUI result")
    plt.show()

    return success

if __name__ == "__main__":
    test_basics()

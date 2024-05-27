from configuration import ROOT_PATH

if __name__ == '__main__':
    with open(f"{ROOT_PATH}/test_pdfs/error.pdf", "rb") as stream:
        files = {"file": stream}
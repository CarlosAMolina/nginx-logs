use std::fmt;

//use lazy_static::lazy_static;
//use regex::Regex;
use serde_derive::Serialize;

#[derive(Debug, PartialEq, Serialize)]
pub struct Log<'a> {
    pub remote_addr: &'a str,
    pub remote_user: &'a str,
    pub time_local: &'a str,
    pub request: &'a str,
    pub status: &'a str,
    pub body_bytes_sent: &'a str,
    pub http_referer: &'a str,
    pub http_user_agent: &'a str,
}

impl<'a> fmt::Display for Log<'a> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "{},{},{},{},{},{},{},{}",
            self.remote_addr,
            self.remote_user,
            self.time_local,
            self.request,
            self.status,
            self.body_bytes_sent,
            self.http_referer,
            self.http_user_agent,
        )
    }
}

// Without regexs
pub fn get_log(text: &str) -> Option<Log> {
    let mut log_parts_index = vec![0];
    let characters_to_match = vec![
        b' ', b' ', b'[', b']', b'"', b'"', b' ', b' ', b'"', b'"', b'"',
    ];
    let bytes = text.as_bytes();
    let mut match_index = 0;
    for (i, &item) in bytes.iter().enumerate() {
        if item == characters_to_match[match_index] {
            log_parts_index.push(i);
            if match_index < characters_to_match.len() - 1 {
                match_index += 1;
            }
        }
    }
    if log_parts_index.len() == 13 {
        Some(Log {
            remote_addr: &text[log_parts_index[0]..log_parts_index[1]],
            remote_user: &text[log_parts_index[2] + 1..log_parts_index[3] - 1],
            time_local: &text[log_parts_index[3] + 1..log_parts_index[4]],
            request: &text[log_parts_index[5] + 1..log_parts_index[6]],
            status: &text[log_parts_index[7] + 1..log_parts_index[8]],
            body_bytes_sent: &text[log_parts_index[8] + 1..log_parts_index[9] - 1],
            http_referer: &text[log_parts_index[9] + 1..log_parts_index[10]],
            http_user_agent: &text[log_parts_index[11] + 1..log_parts_index[12]],
        })
    } else {
        None
    }
}

// Using re.find
//pub fn get_log(text: &str) -> Option<Log> {
//    let mut characters_checked = 0;
//    lazy_static! {
//        static ref RE_IPV4: Regex = Regex::new(r"(\d{1,3}[\.]){3}\d{1,3}",).unwrap();
//    }
//    //ipv4
//    let mut log_parts_index = vec![0];
//    let mut re_result = RE_IPV4.find(text).unwrap();
//    log_parts_index.push(re_result.end());
//    //remote user
//    characters_checked += re_result.end();
//    characters_checked += 3;
//    log_parts_index.push(characters_checked);
//    lazy_static! {
//        static ref RE_REMOTE_USER: Regex = Regex::new(r".+\s\[").unwrap();
//    }
//    re_result = RE_REMOTE_USER.find(&text[characters_checked..]).unwrap();
//    characters_checked += re_result.end();
//    log_parts_index.push(characters_checked - 2);
//    //time local
//    lazy_static! {
//        static ref RE_TIME_LOCAL: Regex =
//            Regex::new(r"\d{2}/[[:alpha:]]{3}/\d{4}:\d{2}:\d{2}:\d{2}\s\+\d{4}",).unwrap();
//    }
//    log_parts_index.push(characters_checked);
//    re_result = RE_TIME_LOCAL.find(&text[characters_checked..]).unwrap();
//    characters_checked += re_result.end();
//    log_parts_index.push(characters_checked);
//    //request
//    characters_checked += 3;
//    log_parts_index.push(characters_checked);
//    lazy_static! {
//        static ref RE_REQUEST: Regex = Regex::new(r#"[[:alpha:]].*"\s\d"#).unwrap();
//    }
//    re_result = RE_REQUEST.find(&text[characters_checked..]).unwrap();
//    characters_checked += re_result.end() - 1;
//    log_parts_index.push(characters_checked - 2);
//    //status
//    log_parts_index.push(characters_checked);
//    characters_checked += 3;
//    log_parts_index.push(characters_checked);
//    //body bytes sent
//    log_parts_index.push(characters_checked + 1);
//    lazy_static! {
//        static ref RE_BODY_BYTES_SENT: Regex = Regex::new(r"\d+").unwrap();
//    }
//    let body_bytes_sent = RE_BODY_BYTES_SENT
//        .find(&text[characters_checked..])
//        .unwrap();
//    characters_checked += body_bytes_sent.end();
//    log_parts_index.push(characters_checked);
//    //http referer
//    characters_checked += 2;
//    log_parts_index.push(characters_checked);
//    lazy_static! {
//        static ref RE_HTTP_REFERER: Regex = Regex::new(r#".*"\s""#).unwrap();
//    }
//    let http_referer = RE_HTTP_REFERER.find(&text[characters_checked..]).unwrap();
//    characters_checked += http_referer.end();
//    log_parts_index.push(characters_checked - 3);
//    //http user agent
//    log_parts_index.push(characters_checked);
//    log_parts_index.push(text.len() - 1);
//    Some(Log {
//        remote_addr: &text[log_parts_index[0]..log_parts_index[1]],
//        remote_user: &text[log_parts_index[2]..log_parts_index[3]],
//        time_local: &text[log_parts_index[4]..log_parts_index[5]],
//        request: &text[log_parts_index[6]..log_parts_index[7]],
//        status: &text[log_parts_index[8]..log_parts_index[9]],
//        body_bytes_sent: &text[log_parts_index[10]..log_parts_index[11]],
//        http_referer: &text[log_parts_index[12]..log_parts_index[13]],
//        http_user_agent: &text[log_parts_index[14]..log_parts_index[15]],
//    })
//}

// Using re.captures
//pub fn get_log(text: &str) -> Option<Log> {
//    lazy_static! {
//        static ref RE: Regex = Regex::new(
//            r#"(?x)
//          ^
//          ((\d{1,3}[\.]){3}\d{1,3}) # IPv4
//          \s-\s
//          (.+)                      # Remote user
//          \s\[
//          (.+)                      # Time local
//          \]\s"
//          (.*)                      # Request
//          "\s
//          (\d{1,3})                 # Status
//          \s
//          (\d+)                     # Body bytes sent
//          \s"
//          (.+)                      # HTTP referer
//          "\s"
//          (.+)                      # HTTP user agent
//          "
//        "#,
//        )
//        .unwrap();
//    }
//    RE.captures(text).and_then(|cap| {
//        let groups = (
//            cap.get(1),
//            cap.get(3),
//            cap.get(4),
//            cap.get(5),
//            cap.get(6),
//            cap.get(7),
//            cap.get(8),
//            cap.get(9),
//        );
//        match groups {
//            (
//                Some(remote_addr),
//                Some(remote_user),
//                Some(time_local),
//                Some(request),
//                Some(status),
//                Some(body_bytes_sent),
//                Some(http_referer),
//                Some(http_user_agent),
//            ) => Some(Log {
//                remote_addr: remote_addr.as_str(),
//                remote_user: remote_user.as_str(),
//                time_local: time_local.as_str(),
//                request: request.as_str(),
//                status: status.as_str(),
//                body_bytes_sent: body_bytes_sent.as_str(),
//                http_referer: http_referer.as_str(),
//                http_user_agent: http_user_agent.as_str(),
//            }),
//            _ => None,
//        }
//    })
//}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_log_for_correct_log() {
        assert_eq!(
            Some(Log{
                remote_addr: "8.8.8.8",
                remote_user: "-",
                time_local: "28/Oct/2021:00:18:22 +0100",
                request: "GET / HTTP/1.1",
                status: "200",
                body_bytes_sent: "77",
                http_referer: "-",
                http_user_agent: "foo bar 1"}
                ),
            get_log("8.8.8.8 - - [28/Oct/2021:00:18:22 +0100] \"GET / HTTP/1.1\" 200 77 \"-\" \"foo bar 1\"")
        );
    }

    #[test]
    fn test_get_log_for_incorrect_log() {
        assert_eq!(
            None,
            get_log("8.8.8.8 - - [28/Oct/2021:00:18:22 +0100 \"GET / HTTP/1.1\" 200 77 \"-\" \"foo bar 1\"")
        );
    }
}
